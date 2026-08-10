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

import pyrogram


class FakeSession:
    MAX_RETRIES = 10

    def __init__(self, *args, **kwargs):
        self.auth_key = args[2]
        self.server_address = kwargs.get("server_address")
        self.port = kwargs.get("port")
        self.is_started = asyncio.Event()

    async def start(self, *args, **kwargs):
        self.is_started.set()

    async def invoke(self, *args, **kwargs):
        return None


class FakeAuth:
    def __init__(self, *args, **kwargs):
        pass

    async def create(self):
        return b"fresh-key"


class FakeClient:
    _get_media_session_pool = pyrogram.Client._get_media_session_pool
    _make_media_session = pyrogram.Client._make_media_session

    def __init__(self):
        self.media_session_pools = {}
        self._media_sessions_locks = {}
        self._session_creation_gate = asyncio.Semaphore(4)
        self.crypto_executor = None
        self.exports = 0

        class Storage:
            async def test_mode(self):
                return False

            async def dc_id(self):
                return 1

            async def auth_key(self):
                return b"home-key"

        self.storage = Storage()

    async def invoke(self, query, *args, **kwargs):
        self.exports += 1
        await asyncio.sleep(0)
        return SimpleNamespace(id=1, bytes=b"exported")

    async def get_session(self, dc_id, is_media=False):
        self.exports += 1
        await asyncio.sleep(0)
        return FakeSession(
            self, dc_id, b"authorized-key", False,
            server_address="media.dc", port=443,
        )


async def test_pool_exports_authorization_once(monkeypatch):
    monkeypatch.setattr(pyrogram.client, "Session", FakeSession)
    monkeypatch.setattr(pyrogram.client, "Auth", FakeAuth)

    client = FakeClient()
    pools = await asyncio.gather(*(client._get_media_session_pool(2, 4) for _ in range(3)))

    assert client.exports == 1

    sessions = pools[0]
    assert len(sessions) == 4
    assert all(s.auth_key == b"authorized-key" for s in sessions)
    assert all(s.server_address == "media.dc" for s in sessions)
    assert all(p == sessions for p in pools)


async def test_pool_grows_without_re_exporting(monkeypatch):
    monkeypatch.setattr(pyrogram.client, "Session", FakeSession)
    monkeypatch.setattr(pyrogram.client, "Auth", FakeAuth)

    client = FakeClient()
    small = await client._get_media_session_pool(2, 2)
    grown = await client._get_media_session_pool(2, 5)

    assert client.exports == 2
    assert len(grown) == 5
    assert grown[:2] == small
