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
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from pyrogram import raw

from .. import utils
from .caching import PEER_CACHE_SIZE
from .remote_storage import SESSION_FIELDS
from .sqlite_storage import SQLiteStorage
from .storage import Storage

log = logging.getLogger(__name__)

SESSION_WRITE = "session"
PEER_WRITE = "peers"
USERNAME_WRITE = "usernames"
STATE_WRITE = "state"
STATE_DELETE = "state_delete"

#: Writes that may be dropped when the queue is full. Losing a peer costs one
#: lookup; losing a session field costs the login, and losing an update state
#: restarts gap recovery from a stale pts.
DROPPABLE = (PEER_WRITE, USERNAME_WRITE)


class HybridStorage(Storage):
    """A local cache in front of a persistent backend.

    Every read is served by a local :obj:`~pyrogram.storage.SQLiteStorage`, so
    ``resolve_peer`` never pays network latency. Writes land locally first and are
    mirrored to the backend by a background task, coalesced by key.

    What that buys, and what it costs:

    - the backend can be slow, or briefly gone, without the client noticing: a
      failed write is retried with backoff and reads keep working;
    - the last few writes live only in the local cache until the writer drains,
      so a hard kill can lose them. ``close()`` flushes; a SIGKILL does not.

    Parameters:
        name (``str``):
            Session name.

        backend (:obj:`~pyrogram.storage.Storage`):
            Where the session is persisted. Usually a
            :obj:`~pyrogram.storage.RemoteStorage` subclass.

        workdir (``Path``, *optional*):
            Where the local cache file goes when *cache_in_memory* is False.

        cache_in_memory (``bool``, *optional*):
            Keep the local cache in memory. Defaults to True. Pass False to keep
            it in a file, which survives a restart and skips the bulk load.

        queue_size (``int``, *optional*):
            Pending backend writes to hold. Defaults to 1024.

        warm_peers (``int``, *optional*):
            How many peers to pull into the cache on open. Defaults to 4096, the
            size of the in-memory peer cache. Pass 0 to fill on demand instead.

        flush_timeout (``float``, *optional*):
            Seconds ``close()`` waits for the queue to drain. Defaults to 10.

        session_string (``str``, *optional*):
            Load this session string into both layers when opening.
    """

    RETRY_DELAY = 1.0
    MAX_RETRY_DELAY = 30.0

    def __init__(
        self,
        name: str,
        backend: Storage,
        workdir: Optional[Path] = None,
        cache_in_memory: bool = True,
        queue_size: int = 1024,
        warm_peers: int = PEER_CACHE_SIZE,
        flush_timeout: float = 10.0,
        session_string: Optional[str] = None,
    ):
        super().__init__(name)

        self.backend = backend
        self.session_string = session_string
        self.flush_timeout = flush_timeout
        self.warm_peers = warm_peers

        self.local = SQLiteStorage(
            name,
            workdir=workdir if workdir is not None else Path.cwd(),
            in_memory=cache_in_memory,
        )

        self._queue: asyncio.Queue = asyncio.Queue(maxsize=queue_size)
        self._writer: Optional[asyncio.Task] = None
        self._closing = False
        self._dropped = 0

    async def open(self) -> None:
        await self.local.open()
        await self.backend.open()

        await self._warm()

        if self.session_string:
            await self.load_session_string(self.session_string)

        self._closing = False
        self._writer = utils.run_in_background(self._writer_loop())

    async def _warm(self) -> None:
        """Copy the backend into the local cache, so every later read is local.

        The peers are the point of this: a client that comes up on a new host with
        an empty cache pays an RPC per peer to rebuild what the backend already
        holds. A backend that cannot enumerate them cheaply returns none, and the
        cache fills on demand instead.
        """
        for field in SESSION_FIELDS:
            value = await getattr(self.backend, field)()

            if value is not None:
                await getattr(self.local, field)(value)

        states = await self.backend.update_state()

        for state in states or ():
            await self.local.update_state(tuple(state))

        export = getattr(self.backend, "export_peers", None)

        if export is None:
            return

        try:
            peers = await export(self.warm_peers)
        except Exception:
            log.warning("Could not warm the peer cache from the backend", exc_info=True)
            return

        if peers:
            await self.local.update_peers(list(peers))
            log.debug("Warmed %s peers from the backend", len(peers))

    def _enqueue(self, kind: str, payload: Any) -> None:
        if self._closing:
            return

        try:
            self._queue.put_nowait((kind, payload))
            return
        except asyncio.QueueFull:
            pass

        self._make_room()
        self._queue.put_nowait((kind, payload))

    def _make_room(self) -> None:
        """Discard the oldest write that is only a cache entry.

        A session field or an update state is never the one dropped: losing a
        peer costs one lookup, losing an auth key costs the login, and losing an
        update state restarts gap recovery from a stale pts. Only when nothing
        droppable is queued does the oldest write of any kind go, since the newer
        one carries the more current value.
        """
        pending = []

        while True:
            try:
                pending.append(self._queue.get_nowait())
            except asyncio.QueueEmpty:
                break

        victim = next((i for i, item in enumerate(pending) if item[0] in DROPPABLE), 0)

        for index, item in enumerate(pending):
            if index != victim:
                self._queue.put_nowait(item)

            self._queue.task_done()

        self._dropped += 1

        log.warning(
            "Hybrid storage write queue is full, dropped %s write(s) so far (last: %s)",
            self._dropped,
            pending[victim][0] if pending else "none",
        )

    async def _writer_loop(self) -> None:
        delay = self.RETRY_DELAY

        while True:
            kind, payload = await self._queue.get()

            try:
                if kind is None:
                    return

                await self._apply(kind, payload)
                delay = self.RETRY_DELAY
            except asyncio.CancelledError:
                raise
            except Exception:
                log.warning(
                    "Hybrid storage backend write failed, retrying in %.0fs", delay, exc_info=True
                )
                await asyncio.sleep(delay)
                delay = min(delay * 2, self.MAX_RETRY_DELAY)

                try:
                    self._queue.put_nowait((kind, payload))
                except asyncio.QueueFull:
                    log.error("Hybrid storage dropped a %s write after a backend failure", kind)
            finally:
                self._queue.task_done()

    async def _apply(self, kind: str, payload: Any) -> None:
        if kind == SESSION_WRITE:
            for attr, value in payload.items():
                await getattr(self.backend, attr)(value)
        elif kind == PEER_WRITE:
            await self.backend.update_peers(payload)
        elif kind == USERNAME_WRITE:
            await self.backend.update_usernames(payload)
        elif kind == STATE_WRITE:
            await self.backend.update_state(payload)
        elif kind == STATE_DELETE:
            await self.backend.update_state(payload)

    async def flush(self, timeout: Optional[float] = None) -> None:
        """Wait for every queued write to reach the backend."""
        timeout = self.flush_timeout if timeout is None else timeout

        try:
            await asyncio.wait_for(self._queue.join(), timeout=timeout)
        except asyncio.TimeoutError:
            log.warning(
                "Hybrid storage still had %s writes queued after %.0fs",
                self._queue.qsize(),
                timeout,
            )

    async def save(self) -> None:
        await self.local.save()
        self._enqueue(SESSION_WRITE, {"date": await self.local.date()})

    async def close(self) -> None:
        # One budget for the whole shutdown, not one per step: a backend that is
        # simply gone would otherwise hold the client up for twice the timeout,
        # and shutdown is exactly when nobody is waiting for it to be thorough.
        deadline = asyncio.get_running_loop().time() + self.flush_timeout

        await self.flush(timeout=self.flush_timeout)

        self._closing = True

        if self._writer is not None:
            remaining = max(0.0, deadline - asyncio.get_running_loop().time())

            try:
                self._queue.put_nowait((None, None))
            except asyncio.QueueFull:
                remaining = 0.0

            if remaining:
                try:
                    await asyncio.wait_for(asyncio.shield(self._writer), timeout=remaining)
                except (asyncio.TimeoutError, asyncio.CancelledError):
                    pass

            if not self._writer.done():
                self._writer.cancel()

            self._writer = None

        await self.local.close()
        await self.backend.close()

    async def delete(self) -> None:
        await self._stop_writer()
        self._drain()

        await self.backend.delete()
        await self.local.delete()

    async def _stop_writer(self) -> None:
        writer, self._writer = self._writer, None

        if writer is None:
            return

        writer.cancel()

        try:
            await writer
        except asyncio.CancelledError:
            pass

    def _drain(self) -> None:
        while True:
            try:
                self._queue.get_nowait()
            except asyncio.QueueEmpty:
                return

            self._queue.task_done()

    async def update_peers(self, peers: List[Tuple[int, int, str, str]]) -> None:
        if not peers:
            return

        await self.local.update_peers(peers)
        self._enqueue(PEER_WRITE, list(peers))

    async def update_usernames(self, usernames: List[Tuple[int, List[str]]]) -> None:
        if not usernames:
            return

        await self.local.update_usernames(usernames)
        self._enqueue(USERNAME_WRITE, list(usernames))

    async def update_state(self, value: Tuple[int, int, int, int, int] = object):
        if value is object:
            return await self.local.update_state()

        await self.local.update_state(value)

        if isinstance(value, int):
            self._enqueue(STATE_DELETE, value)
        else:
            self._enqueue(STATE_WRITE, tuple(value))

        return None

    async def get_peer_by_id(self, peer_id: int) -> "raw.base.InputPeer":
        try:
            return await self.local.get_peer_by_id(peer_id)
        except KeyError:
            pass

        peer = await self.backend.get_peer_by_id(peer_id)

        await self._cache_locally(peer_id)

        return peer

    async def _cache_locally(self, peer_id: int) -> None:
        """Keep what the backend just answered, so the next read is local again.

        Written straight to the local store rather than through ``update_peers``:
        this came *from* the backend, and queueing it would mirror it back.
        """
        fetch = getattr(self.backend, "_fetch_peer", None)

        if fetch is None:
            return

        try:
            stored = await fetch(peer_id)
        except Exception:
            return

        if stored is not None:
            await self.local.update_peers([(stored[0], stored[1], stored[2], None)])

    async def get_peer_by_username(self, username: str) -> "raw.base.InputPeer":
        try:
            return await self.local.get_peer_by_username(username)
        except KeyError:
            return await self.backend.get_peer_by_username(username)

    async def get_peer_by_phone_number(self, phone_number: str) -> "raw.base.InputPeer":
        try:
            return await self.local.get_peer_by_phone_number(phone_number)
        except KeyError:
            return await self.backend.get_peer_by_phone_number(phone_number)

    async def _attr(self, attr: str, value: Any) -> Any:
        if value is object:
            return await getattr(self.local, attr)()

        await getattr(self.local, attr)(value)
        self._enqueue(SESSION_WRITE, {attr: value})

        return value

    async def dc_id(self, value: int = object):
        return await self._attr("dc_id", value)

    async def server_address(self, value: str = object):
        return await self._attr("server_address", value)

    async def port(self, value: int = object):
        return await self._attr("port", value)

    async def api_id(self, value: int = object):
        return await self._attr("api_id", value)

    async def test_mode(self, value: bool = object):
        return await self._attr("test_mode", value)

    async def auth_key(self, value: bytes = object):
        return await self._attr("auth_key", value)

    async def date(self, value: int = object):
        return await self._attr("date", value)

    async def user_id(self, value: int = object):
        return await self._attr("user_id", value)

    async def is_bot(self, value: bool = object):
        return await self._attr("is_bot", value)

    @property
    def dropped_writes(self) -> int:
        return self._dropped
