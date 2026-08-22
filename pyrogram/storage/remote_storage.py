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

import logging
import time
from abc import abstractmethod
from typing import Any, Dict, List, Optional, Tuple

from pyrogram import raw

from .caching import PEER_CACHE_SIZE, PeerRowCache, SessionAttrCache, get_input_peer
from .storage import Storage

log = logging.getLogger(__name__)

SESSION_FIELDS = (
    "dc_id",
    "server_address",
    "port",
    "api_id",
    "test_mode",
    "auth_key",
    "date",
    "user_id",
    "is_bot",
)

DEFAULT_SESSION = {
    "dc_id": 2,
    "server_address": "149.154.167.51",
    "port": 443,
    "api_id": None,
    "test_mode": None,
    "auth_key": None,
    "date": 0,
    "user_id": None,
    "is_bot": None,
}

PeerRow = Tuple[int, int, str, Optional[str]]
StoredPeer = Tuple[int, int, str, int]


class RemoteStorage(Storage):
    """Base for storage engines that keep the session somewhere other than a local file.

    A subclass implements the primitives listed below and gets the whole
    :obj:`~pyrogram.storage.Storage` surface from here, including the two caches
    that keep the hot path off the network:

    - session attributes are read once and then served from memory, so ``dc_id()``
      on every send is a dict lookup rather than a round trip;
    - peer rows are held in a bounded cache, and ``update_peers`` skips peers whose
      access hash has not changed - every ``invoke`` feeds ``r.users`` and
      ``r.chats`` back through ``fetch_peers``, so without that filter the same
      unchanged peers are rewritten on every single RPC.

    ``USERNAME_TTL`` is enforced here, on read, rather than by an expiry feature of
    the store: a backend that drops the row itself would disagree with what the
    SQLite engine does with a stale one.
    """

    VERSION = 1
    USERNAME_TTL = 8 * 60 * 60

    def __init__(self, name: str, session_string: Optional[str] = None):
        super().__init__(name)

        self.session_string = session_string

        self._cache = SessionAttrCache()
        self._peer_cache = PeerRowCache(PEER_CACHE_SIZE)
        self._opened = False

    @abstractmethod
    async def _connect(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def _disconnect(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def _load_session(self) -> Optional[Dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    async def _save_session(self, fields: Dict[str, Any]) -> None:
        raise NotImplementedError

    @abstractmethod
    async def _upsert_peers(self, rows: List[PeerRow]) -> None:
        raise NotImplementedError

    @abstractmethod
    async def _fetch_peer(self, peer_id: int) -> Optional[StoredPeer]:
        raise NotImplementedError

    @abstractmethod
    async def _fetch_peer_by_username(self, username: str) -> Optional[StoredPeer]:
        raise NotImplementedError

    @abstractmethod
    async def _fetch_peer_by_phone(self, phone_number: str) -> Optional[StoredPeer]:
        raise NotImplementedError

    @abstractmethod
    async def _replace_usernames(self, usernames: List[Tuple[int, List[str]]]) -> None:
        raise NotImplementedError

    @abstractmethod
    async def _load_states(self) -> List[Tuple[int, int, int, int, int]]:
        raise NotImplementedError

    @abstractmethod
    async def _save_state(self, state: Tuple[int, int, int, int, int]) -> None:
        raise NotImplementedError

    @abstractmethod
    async def _delete_state(self, state_id: int) -> None:
        raise NotImplementedError

    @abstractmethod
    async def _purge(self, remove_peers: bool) -> None:
        raise NotImplementedError

    async def _iter_peers(self, limit: Optional[int] = None) -> List[PeerRow]:
        """Peers held by this backend, newest first.

        Optional: it exists so :obj:`~pyrogram.storage.HybridStorage` can fill its
        local cache on open, which is the difference between a restarted client
        resolving peers from memory and paying an RPC each. A backend that cannot
        enumerate cheaply should leave this returning an empty list.
        """
        return []

    async def _load_version(self) -> Optional[int]:
        return None

    async def _save_version(self, version: int) -> None:
        return None

    async def _migrate(self, version: int) -> None:
        return None

    async def open(self) -> None:
        if self._opened:
            return

        await self._connect()
        self._opened = True

        stored = await self._load_session()

        if stored is None:
            await self._save_session(dict(DEFAULT_SESSION))
            await self._save_version(self.VERSION)
            self._cache.load(dict(DEFAULT_SESSION))
        else:
            version = await self._load_version()

            if version is not None and version < self.VERSION:
                await self._migrate(version)
                await self._save_version(self.VERSION)
                stored = await self._load_session() or dict(DEFAULT_SESSION)

            for field in SESSION_FIELDS:
                self._cache.remember(field, stored.get(field))

        if self.session_string:
            await self.load_session_string(self.session_string)

    async def save(self) -> None:
        await self.date(int(time.time()))

    async def close(self) -> None:
        if not self._opened:
            return

        self._opened = False
        self._cache.clear()
        self._peer_cache.clear()

        await self._disconnect()

    async def delete(self, remove_peers: bool = True) -> None:
        await self._purge(remove_peers)

        self._cache.clear()
        self._peer_cache.clear()

    async def update_peers(self, peers: List[PeerRow]) -> None:
        if not peers:
            return

        fresh = [p for p in peers if not self._peer_cache.matches(p[0], p[1], p[2])]

        if not fresh:
            return

        await self._upsert_peers(fresh)

        for peer_id, access_hash, peer_type, _ in fresh:
            self._peer_cache.remember((peer_id, access_hash, peer_type))

    async def update_usernames(self, usernames: List[Tuple[int, List[str]]]) -> None:
        if not usernames:
            return

        await self._replace_usernames(usernames)

    async def update_state(
        self, value: Tuple[int, int, int, int, int] = object
    ) -> Optional[List[Tuple[int, int, int, int, int]]]:
        if value is object:
            return await self._load_states()

        if isinstance(value, int):
            await self._delete_state(value)
            return None

        await self._save_state(tuple(value))
        return None

    async def get_peer_by_id(self, peer_id: int) -> "raw.base.InputPeer":
        row = self._peer_cache.get(peer_id)

        if row is not None:
            return get_input_peer(*row)

        stored = await self._fetch_peer(peer_id)

        if stored is None:
            raise KeyError(f"ID not found: {peer_id}")

        row = tuple(stored[:3])
        self._peer_cache.remember(row)

        return get_input_peer(*row)

    async def get_peer_by_username(self, username: str) -> "raw.base.InputPeer":
        stored = await self._fetch_peer_by_username(username)

        if stored is None:
            raise KeyError(f"Username not found: {username}")

        if abs(time.time() - stored[3]) > self.USERNAME_TTL:
            raise KeyError(f"Username expired: {username}")

        return get_input_peer(*stored[:3])

    async def get_peer_by_phone_number(self, phone_number: str) -> "raw.base.InputPeer":
        stored = await self._fetch_peer_by_phone(phone_number)

        if stored is None:
            raise KeyError(f"Phone number not found: {phone_number}")

        return get_input_peer(*stored[:3])

    async def export_peers(self, limit: Optional[int] = None) -> List[PeerRow]:
        """Peers this backend holds, for warming a cache in front of it."""
        return await self._iter_peers(limit)

    async def _read_attr(self, attr: str) -> Any:
        if not self._opened:
            raise ConnectionError("Storage is not open")

        if attr in self._cache:
            return self._cache.get(attr)

        stored = await self._load_session() or {}
        self._cache.remember(attr, stored.get(attr))

        return self._cache.get(attr)

    async def _write_attr(self, attr: str, value: Any) -> None:
        if not self._opened:
            raise ConnectionError("Storage is not open")

        await self._save_session({attr: value})
        self._cache.set(attr, value)

    async def dc_id(self, value: int = object):
        if value is object:
            return await self._read_attr("dc_id")
        await self._write_attr("dc_id", value)
        return value

    async def server_address(self, value: str = object):
        if value is object:
            return await self._read_attr("server_address")
        await self._write_attr("server_address", value)
        return value

    async def port(self, value: int = object):
        if value is object:
            return await self._read_attr("port")
        await self._write_attr("port", value)
        return value

    async def api_id(self, value: int = object):
        if value is object:
            return await self._read_attr("api_id")
        await self._write_attr("api_id", value)
        return value

    async def test_mode(self, value: bool = object):
        if value is object:
            return await self._read_attr("test_mode")
        await self._write_attr("test_mode", value)
        return value

    async def auth_key(self, value: bytes = object):
        if value is object:
            return await self._read_attr("auth_key")
        await self._write_attr("auth_key", value)
        return value

    async def date(self, value: int = object):
        if value is object:
            return await self._read_attr("date")
        await self._write_attr("date", value)
        return value

    async def user_id(self, value: int = object):
        if value is object:
            return await self._read_attr("user_id")
        await self._write_attr("user_id", value)
        return value

    async def is_bot(self, value: bool = object):
        if value is object:
            return await self._read_attr("is_bot")
        await self._write_attr("is_bot", value)
        return value

    async def version(self, value: int = object):
        if value is object:
            return await self._load_version()
        await self._save_version(value)
        return value
