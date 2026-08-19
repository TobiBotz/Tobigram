import asyncio
import logging
from types import SimpleNamespace

import pytest

import pyrogram
from pyrogram.methods.auth.terminate import Terminate
from pyrogram.methods.utilities.stop import Stop
from pyrogram.session import Session
from pyrogram.types import ListenerRegistry


class FakeSession:
    MAX_RETRIES = 10

    def __init__(self, *args, **kwargs):
        self.auth_key = args[2]
        self.is_media = kwargs.get("is_media", False)
        self.is_started = asyncio.Event()
        self.stopped = False

    async def start(self, *args, **kwargs):
        self.is_started.set()

    async def stop(self):
        self.stopped = True
        self.is_started.clear()

    async def invoke(self, *args, **kwargs):
        return None


class FakeAuth:
    def __init__(self, *args, **kwargs):
        pass

    async def create(self):
        return b"fresh-key"


class FakeClient(Terminate):
    get_session = pyrogram.Client.get_session

    def __init__(self):
        self.is_initialized = True
        self.takeout_id = None
        self.ipv6 = False
        self.crypto_executor = None
        self.rate_limiter = None
        self.executor = None
        self.business_connections = {}
        self.sessions = {}
        self.media_sessions = {}
        self.media_session_pools = {}
        self._session_locks = {}
        self._media_sessions_locks = {}
        self._session_creation_gate = asyncio.Semaphore(4)
        self.updates_watchdog_event = asyncio.Event()
        self.updates_watchdog_task = None
        self.media_pool_reaper_event = asyncio.Event()
        self.media_pool_reaper_task = None
        self.listeners = ListenerRegistry(self)
        self.dispatcher = SimpleNamespace(stop=self._noop)
        self.session = FakeSession(self, 1, b"home-key", False)

        class Storage:
            async def save(self):
                pass

            async def test_mode(self):
                return False

            async def dc_id(self):
                return 1

            async def auth_key(self):
                return b"home-key"

        self.storage = Storage()

    async def _noop(self):
        pass

    async def get_dc_option(self, dc_id=None, is_media=False, is_cdn=False, ipv6=False):
        return SimpleNamespace(ip_address=f"10.0.0.{dc_id}", port=443)

    async def invoke(self, query, *args, **kwargs):
        await asyncio.sleep(0)
        return SimpleNamespace(id=1, bytes=b"exported")


@pytest.fixture(autouse=True)
def _stub_session(monkeypatch):
    monkeypatch.setattr(pyrogram.client, "Session", FakeSession)
    monkeypatch.setattr(pyrogram.client, "Auth", FakeAuth)


async def test_a_media_session_caches_a_non_media_session_too():
    client = FakeClient()
    await client.get_session(4, is_media=True)

    assert list(client.media_sessions) == [4]
    assert list(client.sessions) == [4]


async def test_terminate_stops_every_cached_session():
    client = FakeClient()
    await client.get_session(4, is_media=True)
    client.media_session_pools[4] = [FakeSession(client, 4, b"pool-key", False, is_media=True)]

    cached = [
        *client.sessions.values(),
        *client.media_sessions.values(),
        *(s for pool in client.media_session_pools.values() for s in pool),
    ]
    assert len(cached) == 3

    await client.terminate()

    assert all(s.stopped for s in cached)
    assert not client.sessions
    assert not client.media_sessions
    assert not client.media_session_pools


async def test_stopping_a_cached_session_does_not_fire_the_disconnect_handler():
    fired = []

    async def on_disconnect(client):
        fired.append(client)

    client = SimpleNamespace(
        session=None, disconnect_handler=on_disconnect, ipv6=False, proxy=None
    )

    main = Session(client, 1, b"k" * 256, False)
    client.session = main
    cached = Session(client, 4, b"k" * 256, False)

    await cached.stop()
    assert fired == []

    await main.stop()
    assert fired == [client]


class StoppingClient(Stop):
    """A client that connected but never finished starting up.

    A bad session string leaves exactly this state: connect() succeeded, start()
    raised before initialize(), and the caller still has to stop it.
    """

    def __init__(self, is_initialized, is_connected):
        self.is_initialized = is_initialized
        self.is_connected = is_connected
        self.terminated = False
        self.disconnected = False
        self.loop = asyncio.get_event_loop()

    async def terminate(self):
        if not self.is_initialized:
            raise ConnectionError("Client is already terminated")

        self.terminated = True
        self.is_initialized = False

    async def disconnect(self):
        if not self.is_connected:
            raise ConnectionError("Client is already disconnected")

        if self.is_initialized:
            raise ConnectionError("Can not disconnect an initialized client")

        self.disconnected = True
        self.is_connected = False


async def test_stopping_a_half_started_client_still_disconnects_it(caplog):
    client = StoppingClient(is_initialized=False, is_connected=True)

    with caplog.at_level(logging.ERROR):
        await client.stop()

    assert client.disconnected, (
        "terminate raising ConnectionError used to abandon the socket, because "
        "both calls shared one try block"
    )
    assert not caplog.records, (
        "a client that never finished starting up is not an error to report"
    )


async def test_stopping_a_started_client_does_both():
    client = StoppingClient(is_initialized=True, is_connected=True)

    await client.stop()

    assert client.terminated and client.disconnected


async def test_stopping_an_already_stopped_client_is_quiet(caplog):
    client = StoppingClient(is_initialized=False, is_connected=False)

    with caplog.at_level(logging.ERROR):
        await client.stop()

    assert not caplog.records
    assert not client.terminated and not client.disconnected
