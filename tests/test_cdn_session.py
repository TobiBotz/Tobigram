import asyncio
import inspect
from types import SimpleNamespace

import pyrogram
from pyrogram import raw


class FakeSession:
    MAX_RETRIES = 10

    def __init__(self, *args, **kwargs):
        self.auth_key = args[2]
        self.is_media = kwargs.get("is_media")
        self.is_cdn = kwargs.get("is_cdn")
        self.server_address = kwargs.get("server_address")
        self.port = kwargs.get("port")
        self.is_started = asyncio.Event()

    async def start(self, *args, **kwargs):
        self.is_started.set()

    async def invoke(self, *args, **kwargs):
        return None


class FakeAuth:
    def __init__(self, client, dc_id, test_mode, server_address=None, port=None):
        self.dc_id = dc_id
        self.server_address = server_address

    async def create(self):
        return b"cdn-key"


class FakeClient:
    get_session = pyrogram.Client.get_session

    def __init__(self):
        self.sessions = {}
        self.media_sessions = {}
        self._session_locks = {}
        self._session_creation_gate = asyncio.Semaphore(4)
        self.crypto_executor = None
        self.ipv6 = False
        self.business_connections = {}
        self.invoked = []

        class Storage:
            async def test_mode(self):
                return False

            async def dc_id(self):
                return 1

            async def auth_key(self):
                return b"home-key"

        self.storage = Storage()

    async def invoke(self, query, *args, **kwargs):
        self.invoked.append(type(query).__name__)
        await asyncio.sleep(0)
        return SimpleNamespace(id=1, bytes=b"exported")

    async def get_dc_option(self, dc_id, is_media=False, is_cdn=False, ipv6=False):
        return SimpleNamespace(ip_address=f"cdn{dc_id}.telegram", port=443)


async def _cdn_session(monkeypatch):
    monkeypatch.setattr(pyrogram.client, "Session", FakeSession)
    monkeypatch.setattr(pyrogram.client, "Auth", FakeAuth)

    client = FakeClient()
    session = await client.get_session(203, is_media=True, is_cdn=True, temporary=True)
    return client, session


async def test_cdn_session_is_marked_as_cdn(monkeypatch):
    _, session = await _cdn_session(monkeypatch)

    assert session.is_cdn is True
    assert session.is_media is True


async def test_cdn_session_uses_its_own_auth_key(monkeypatch):
    _, session = await _cdn_session(monkeypatch)

    assert session.auth_key == b"cdn-key"
    assert session.server_address == "cdn203.telegram"


async def test_cdn_session_does_not_import_authorization(monkeypatch):
    client, _ = await _cdn_session(monkeypatch)

    assert raw.functions.auth.ExportAuthorization.__name__ not in client.invoked


def test_cdn_redirect_carries_its_own_dc_id():
    assert "dc_id" in raw.types.upload.FileCdnRedirect.__slots__


def test_get_file_connects_to_the_redirected_dc():
    source = " ".join(inspect.getsource(pyrogram.Client.get_file).split())

    assert "cdn_session = await self.get_session( r.dc_id," in source
