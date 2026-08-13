import asyncio
from types import SimpleNamespace

import pytest

import pyrogram
from pyrogram import raw
from pyrogram.errors import PhoneMigrate, UserMigrate
from pyrogram.methods.auth.connect import Connect
from pyrogram.methods.auth.send_code import SendCode
from pyrogram.methods.auth.sign_in_bot import SignInBot


class FakeSession:
    def __init__(self, *args, **kwargs):
        self.auth_key = args[2]
        self.server_address = kwargs.get("server_address")
        self.port = kwargs.get("port")

    async def start(self, *args, **kwargs):
        pass

    async def stop(self):
        pass


class FakeStorage:
    def __init__(self, **values):
        self.values = {
            "dc_id": 2,
            "server_address": "10.0.0.2",
            "port": 443,
            "auth_key": b"k" * 256,
            "test_mode": False,
            "user_id": 7,
            **values,
        }

    def __getattr__(self, name):
        async def accessor(value=object):
            if value is object:
                return self.values[name]
            self.values[name] = value
            return value

        return accessor


class FakeClient(Connect, SendCode, SignInBot):
    def __init__(self, ipv6=False, migrate=None):
        self.is_connected = False
        self.ipv6 = ipv6
        self.crypto_executor = None
        self.storage = FakeStorage()
        self.session = FakeSession(self, 2, b"old", False)
        self.migrate = migrate
        self.api_id = 1
        self.api_hash = "h"
        self.requested_dc_options = []

    async def load_session(self):
        pass

    async def get_dc_option(self, dc_id, is_media=False, is_cdn=False, ipv6=False):
        self.requested_dc_options.append(dc_id)
        return SimpleNamespace(ip_address=f"10.0.0.{dc_id}", port=443)

    async def get_session(self, dc_id=None, server_address=None, port=None, **kwargs):
        return FakeSession(
            self, dc_id, b"migrated-key", False,
            server_address=server_address, port=port,
        )

    async def invoke(self, query, *args, **kwargs):
        await asyncio.sleep(0)
        if self.migrate is not None:
            exc, self.migrate = self.migrate, None
            raise exc
        return SimpleNamespace(
            user=SimpleNamespace(id=7),
            type=raw.types.auth.SentCodeTypeApp(length=5),
            phone_code_hash="hash",
            next_type=None,
            timeout=None,
        )


@pytest.fixture(autouse=True)
def _stub_session(monkeypatch):
    monkeypatch.setattr(pyrogram.methods.auth.connect, "Session", FakeSession)


async def test_connect_uses_the_stored_address():
    client = FakeClient()
    await client.connect()

    assert client.session.server_address == "10.0.0.2"
    assert client.session.port == 443


async def test_connect_ignores_an_address_of_the_wrong_family():
    client = FakeClient(ipv6=True)
    await client.connect()

    assert client.session.server_address is None
    assert client.session.port is None


async def test_connect_falls_back_when_nothing_is_stored():
    client = FakeClient()
    client.storage.values["server_address"] = None
    client.storage.values["port"] = None
    await client.connect()

    assert client.session.server_address is None


async def test_send_code_migration_keeps_dc_and_address_in_step():
    client = FakeClient(migrate=PhoneMigrate(value=4))
    await client.send_code("+10000000000")

    assert client.storage.values["dc_id"] == 4
    assert client.storage.values["server_address"] == "10.0.0.4"
    assert client.storage.values["auth_key"] == b"migrated-key"


async def test_sign_in_bot_migration_keeps_dc_and_address_in_step():
    client = FakeClient(migrate=UserMigrate(value=5))
    await client.sign_in_bot("token")

    assert client.storage.values["dc_id"] == 5
    assert client.storage.values["server_address"] == "10.0.0.5"
    assert client.storage.values["auth_key"] == b"migrated-key"
