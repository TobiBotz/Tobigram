#  Pyrogram - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-present Dan <https://github.com/delivrance>
#
#  This file is part of Pyrogram.
#
#  Pyrogram is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Pyrogram is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with Pyrogram.  If not, see <http://www.gnu.org/licenses/>.

import asyncio
import functools
import inspect
import io
import logging
import math
import os
import time
from hashlib import md5
from pathlib import PurePath
from typing import Union, BinaryIO, Callable, Optional

import pyrogram
from pyrogram import StopTransmission
from pyrogram import raw

log = logging.getLogger(__name__)

PART_SIZE = 512 * 1024
WORKERS_PER_SESSION = 4
POOL_SIZE = 4
MAX_RETRIES = 5
READ_BUFFER = 4 * 1024 * 1024
PROGRESS_INTERVAL = 0.1


class SaveFile:
    async def save_file(
        self: "pyrogram.Client",
        path: Union[str, BinaryIO],
        file_id: Optional[int] = None,
        file_part: int = 0,
        progress: Optional[Callable] = None,
        progress_args: tuple = (),
    ):
        """Upload a file onto Telegram servers, without sending the message to anyone.

        Useful whenever an InputFile type is required for raw API functions.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            path (``str`` | ``BinaryIO``):
                File path or binary file-like object.

            file_id (``int``, *optional*):
                File ID to resume an interrupted upload.

            file_part (``int``, *optional*):
                Part number to resume from.

            progress (``Callable``, *optional*):
                Callback — takes *(current, total)* as positional arguments.

            progress_args (``tuple``, *optional*):
                Extra arguments for the progress callback.

        Returns:
            ``InputFile | InputFileBig``: On success.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        async with self.save_file_semaphore:
            if path is None:
                return None

            async def worker(session):
                while True:
                    data = await queue.get()

                    if data is None:
                        return

                    for attempt in range(MAX_RETRIES):
                        try:
                            await session.invoke(data)
                            break
                        except StopTransmission:
                            raise
                        except Exception as e:
                            if attempt == MAX_RETRIES - 1:
                                log.error(
                                    f"Upload part failed after "
                                    f"{MAX_RETRIES} attempts: {e}"
                                )
                                raise
                            log.warning(
                                f"Retrying upload part "
                                f"(attempt {attempt + 1}/{MAX_RETRIES}): {e}"
                            )
                            await asyncio.sleep(2**attempt)

            async def read_chunk():
                return await self.loop.run_in_executor(
                    self.executor, fp.read, PART_SIZE
                )

            part_size = PART_SIZE

            if isinstance(path, (str, PurePath)):
                fp = open(path, "rb", buffering=READ_BUFFER)
            elif isinstance(path, io.IOBase):
                fp = path
            else:
                raise ValueError(
                    "Invalid file. Expected a file path as string "
                    "or a binary (not text) file pointer"
                )

            file_name = getattr(fp, "name", "file.jpg")

            fp.seek(0, os.SEEK_END)
            file_size = fp.tell()
            fp.seek(0)

            if file_size == 0:
                raise ValueError("File size equals to 0 B")

            file_size_limit_mib = 4000 if self.me.is_premium else 2000

            if file_size > file_size_limit_mib * 1024 * 1024:
                raise ValueError(
                    f"Can't upload files bigger than {file_size_limit_mib} MiB"
                )

            file_total_parts = int(math.ceil(file_size / part_size))
            is_big = file_size > 10 * 1024 * 1024
            pool_size = POOL_SIZE if is_big else 1
            workers_count = WORKERS_PER_SESSION if is_big else 1
            is_missing_part = file_id is not None
            file_id = file_id or self.rnd_id()
            md5_sum = md5() if not is_big and not is_missing_part else None

            dc_id = await self.storage.dc_id()
            pool = await self._get_media_session_pool(dc_id, pool_size)

            n_sessions = len(pool)
            n_workers = n_sessions * workers_count
            queue = asyncio.Queue(n_workers)
            workers = [
                self.loop.create_task(worker(pool[i % n_sessions]))
                for i in range(n_workers)
            ]
            next_chunk_task = None
            _last_progress_time = 0.0

            try:

                fp.seek(part_size * file_part)
                next_chunk_task = self.loop.create_task(read_chunk())

                while True:
                    chunk = await next_chunk_task
                    next_chunk_task = self.loop.create_task(read_chunk())

                    if not chunk:
                        next_chunk_task.cancel()
                        if not is_big and not is_missing_part:
                            md5_sum = md5_sum.hexdigest()
                        break

                    if all(t.done() for t in workers):
                        for t in workers:
                            exc = t.exception()
                            if exc is not None:
                                raise exc
                        raise RuntimeError("All upload workers exited")

                    if is_big:
                        rpc = raw.functions.upload.SaveBigFilePart(
                            file_id=file_id,
                            file_part=file_part,
                            file_total_parts=file_total_parts,
                            bytes=chunk,
                        )
                    else:
                        rpc = raw.functions.upload.SaveFilePart(
                            file_id=file_id, file_part=file_part, bytes=chunk
                        )

                    await queue.put(rpc)

                    if is_missing_part:
                        next_chunk_task.cancel()
                        for _ in range(n_workers):
                            await queue.put(None)
                        results = await asyncio.gather(*workers, return_exceptions=True)
                        for r in results:
                            if isinstance(r, BaseException) and not isinstance(
                                r, asyncio.CancelledError
                            ):
                                raise r
                        return None

                    if not is_big and not is_missing_part:
                        md5_sum.update(chunk)

                    file_part += 1

                    if progress:
                        _now = time.monotonic()
                        if _now - _last_progress_time >= PROGRESS_INTERVAL:
                            _last_progress_time = _now

                            _sent = min(file_part * part_size, file_size)
                            _total = file_size

                            async def report(_sent=_sent, _total=_total):
                                try:
                                    if inspect.iscoroutinefunction(progress):
                                        await progress(_sent, _total, *progress_args)
                                    else:
                                        await self.loop.run_in_executor(
                                            self.executor,
                                            functools.partial(
                                                progress, _sent, _total, *progress_args
                                            ),
                                        )
                                except Exception as e:
                                    log.warning(f"Progress callback error: {e}")

                            asyncio.ensure_future(report())

            except StopTransmission:
                raise
            except Exception as e:
                log.exception(e)
                raise
            else:
                if is_big:
                    return raw.types.InputFileBig(
                        id=file_id,
                        parts=file_total_parts,
                        name=file_name,
                    )
                else:
                    return raw.types.InputFile(
                        id=file_id,
                        parts=file_total_parts,
                        name=file_name,
                        md5_checksum=md5_sum,
                    )
            finally:
                if next_chunk_task is not None and not next_chunk_task.done():
                    next_chunk_task.cancel()

                for _ in workers:
                    await queue.put(None)

                await asyncio.gather(*workers)

                if isinstance(path, (str, PurePath)):
                    fp.close()
