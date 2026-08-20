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
from types import SimpleNamespace

import pytest

import pyrogram
from pyrogram import raw
from pyrogram.file_id import FileType

CHUNK = 1024 * 1024


class FakeSession:
    def __init__(self, chunks):
        self.chunks = list(chunks)

    async def invoke(self, query, **kwargs):
        offset = query.offset
        index = offset // CHUNK
        data = self.chunks[index] if index < len(self.chunks) else b""
        return raw.types.upload.File(
            type=raw.types.storage.FileUnknown(),
            mtime=0,
            bytes=data,
        )


class FakeClient:
    get_file = pyrogram.Client.get_file
    handle_download = pyrogram.Client.handle_download
    read_ahead_slots = pyrogram.Client.read_ahead_slots
    MAX_READ_AHEAD_CHUNKS = pyrogram.Client.MAX_READ_AHEAD_CHUNKS

    def __init__(self, chunks):
        self.get_file_semaphore = asyncio.Semaphore(1)
        self.me = SimpleNamespace(is_bot=True, is_premium=False)
        self.session = FakeSession(chunks)

    async def get_session(self, dc_id, is_media=False):
        return self.session

    async def _get_media_session_pool(self, dc_id, size):
        return [self.session]


def file_id():
    return SimpleNamespace(
        file_type=FileType.DOCUMENT,
        media_id=1,
        access_hash=1,
        file_reference=b"",
        thumbnail_size="",
        dc_id=2,
    )


async def download(tmp_path, chunks, file_size):
    client = FakeClient(chunks)
    path = await client.handle_download(
        (file_id(), str(tmp_path), "out.bin", False, file_size, None, ())
    )
    with open(path, "rb") as f:
        return f.read()


@pytest.mark.parametrize(
    "chunks",
    [
        [b"x" * 2048],                        # single short chunk
        [b"a" * CHUNK, b"b" * 4096],          # spills into the sequential loop
    ],
)
async def test_unknown_size_download_is_written(tmp_path, chunks):
    # Telegram reports file_size 0 for some media; the bytes must still land on disk.
    assert await download(tmp_path, chunks, 0) == b"".join(chunks)


async def test_known_size_download_is_written(tmp_path):
    data = b"x" * 2048
    assert await download(tmp_path, [data], len(data)) == data


class ShortAfterFirstSession(FakeSession):
    """A datacentre that answers every part after the first with a short one."""

    def __init__(self):
        self.served = 0

    async def invoke(self, query, **kwargs):
        self.served += 1
        return raw.types.upload.File(
            type=raw.types.storage.FileUnknown(),
            mtime=0,
            bytes=b"x" * (CHUNK if query.offset == 0 else CHUNK // 2),
        )


async def test_a_download_ends_when_its_workers_do(tmp_path):
    # every parallel worker retires on its first short part, so offsets are left
    # unclaimed and the completion count never reaches the chunk count
    client = FakeClient([])
    client.session = ShortAfterFirstSession()

    path = await asyncio.wait_for(
        client.handle_download(
            (file_id(), str(tmp_path), "out.bin", False, 20 * CHUNK, None, ())
        ),
        timeout=10,
    )

    assert path is not None
