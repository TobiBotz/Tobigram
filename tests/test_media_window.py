import asyncio
from types import SimpleNamespace

import pyrogram
import pyrogram.session.session as session_mod
from pyrogram import raw
from pyrogram.errors import ServiceUnavailable
from pyrogram.session.session import MediaWindow, Session, media_window
from tests.test_stability import DummyClient


def test_a_window_starts_at_one_connection():
    assert MediaWindow().connections(16, now=0) == 1


def test_a_window_grows_by_one_after_a_quiet_spell():
    window = MediaWindow()
    window.connections(16, now=0)

    assert window.connections(16, now=MediaWindow.GROW_AFTER - 1) == 1
    assert window.connections(16, now=MediaWindow.GROW_AFTER + 1) == 2
    assert window.connections(16, now=MediaWindow.GROW_AFTER + 2) == 2, (
        "growing on every call would open connections in a burst, which is the "
        "thing a media DC drops"
    )


def test_a_window_does_not_grow_past_what_is_asked_of_it():
    window = MediaWindow()

    for t in range(0, 100_000, 1_000):
        window.connections(1, now=t)

    assert window.connections(16, now=100_001) <= 2, (
        "an idle window that kept growing would open a burst of connections on the next transfer"
    )


def test_a_drop_halves_the_window_once_per_burst():
    window = MediaWindow()
    window.size = 8

    window.shrink(now=100)
    assert window.size == 4

    window.shrink(now=100.5)
    assert window.size == 4, "one burst of closes is one signal, not one per socket"

    window.shrink(now=100 + MediaWindow.SHRINK_COOLDOWN + 1)
    assert window.size == 2

    for t in range(200, 300, 10):
        window.shrink(now=t)
    assert window.size == 1


def test_a_drop_resets_the_quiet_spell():
    window = MediaWindow()
    window.size = 4
    window.shrink(now=1000)

    assert window.connections(16, now=1000 + MediaWindow.GROW_AFTER - 1) == 2


def test_a_fixed_window_gives_what_is_asked_and_never_shrinks():
    window = MediaWindow()
    window.fixed = True

    assert window.connections(6, now=0) == 6
    window.shrink(now=10)
    assert window.connections(6, now=11) == 6
    assert window.size == 6


async def test_a_premium_pool_opens_every_connection_at_once(monkeypatch):
    client = pyrogram.Client("premium", api_id=1, api_hash="x", in_memory=True)
    client.me = SimpleNamespace(is_premium=True)
    media = PoolSession()

    async def get_session(dc_id, is_media=False, **kwargs):
        return media

    async def make(dc_id, auth_key, server_address=None, port=None):
        return PoolSession()

    monkeypatch.setattr(client, "get_session", get_session)
    monkeypatch.setattr(client, "_make_media_session", make)

    pool = await client._get_media_session_pool(42, 6)

    assert len(pool) == 6 and pool[0] is media


def test_windows_are_per_key_and_dc():
    a = media_window(b"k" * 256, 2)

    assert media_window(b"k" * 256, 2) is a
    assert media_window(b"k" * 256, 4) is not a
    assert media_window(b"j" * 256, 2) is not a


class ClosingConnection:
    protocol = SimpleNamespace(crypto_executor=None)

    async def recv(self):
        return None

    async def close(self):
        pass


def fresh_session(dc_id, is_media=True):
    key = bytes([dc_id]) * 256
    session = Session(DummyClient(), dc_id, key, False, is_media=is_media, crypto_executor=None)
    session_mod._media_windows.pop((session.auth_key, dc_id), None)
    return session


async def test_a_media_connection_closed_by_the_server_shrinks_its_window():
    session = fresh_session(31)
    window = media_window(session.auth_key, 31)
    window.size = 4
    session.connection = ClosingConnection()

    await session.recv_worker()

    assert window.size == 2


async def test_a_control_connection_closing_leaves_the_media_window_alone():
    session = fresh_session(32, is_media=False)
    window = media_window(session.auth_key, 32)
    window.size = 4
    session.connection = ClosingConnection()

    await session.recv_worker()

    assert window.size == 4


def get_file():
    return raw.functions.upload.GetFile(
        location=raw.types.InputDocumentFileLocation(
            id=1, access_hash=1, file_reference=b"", thumb_size=""
        ),
        offset=0,
        limit=1024 * 1024,
    )


async def test_a_503_backs_off_and_shrinks_the_window(monkeypatch):
    session = fresh_session(33)
    window = media_window(session.auth_key, 33)
    window.size = 4
    session.is_started.set()
    calls = 0

    async def send(query, wait_response=True, timeout=None, retry=0):
        nonlocal calls
        calls += 1
        if calls < 5:
            raise ServiceUnavailable(rpc_name="upload.GetFile")
        return "ok"

    slept = []

    async def sleep(delay):
        slept.append(delay)

    session.send = send
    monkeypatch.setattr(session_mod.asyncio, "sleep", sleep)

    assert await session.invoke(get_file()) == "ok"
    assert slept == sorted(slept) and slept[-1] > slept[0], (
        f"retries slept {slept}; a flat delay re-sends into an overloaded DC in lockstep"
    )
    assert window.size < 4


class PoolSession:
    def __init__(self, auth_key_id=b"p" * 8):
        self.auth_key = b"p" * 256
        self.auth_key_id = auth_key_id
        self.server_address = "x"
        self.port = 443
        self.results = {}
        self.last_used = 0.0
        self.is_restarting = False
        self.is_started = asyncio.Event()
        self.is_started.set()
        self.stopped = False

    async def stop(self):
        self.stopped = True


async def test_the_pool_is_the_window_and_counts_the_main_media_connection(monkeypatch):
    client = pyrogram.Client("window", api_id=1, api_hash="x", in_memory=True)
    media = PoolSession()
    made = []

    async def get_session(dc_id, is_media=False, **kwargs):
        return media

    async def make(dc_id, auth_key, server_address=None, port=None):
        made.append(PoolSession())
        return made[-1]

    monkeypatch.setattr(client, "get_session", get_session)
    monkeypatch.setattr(client, "_make_media_session", make)

    window = media_window(media.auth_key, 41)
    window.size = 1
    pool = await client._get_media_session_pool(41, 5)

    assert pool == [media], f"{len(pool)} connections with a window of one"
    assert made == []

    window.size = 3
    pool = await client._get_media_session_pool(41, 5)

    assert pool[0] is media and len(pool) == 3

    window.size = 1
    pool = await client._get_media_session_pool(41, 5)

    assert pool == [media]
    await asyncio.sleep(0)
    assert all(s.stopped for s in made), (
        "connections above a shrunk window stay open and keep the DC dropping them"
    )


async def test_a_transfer_never_picks_a_connection_stopped_under_it(monkeypatch):
    from tests.test_stability import CHUNK, SharedLink, link_client
    from pyrogram.file_id import FileId, FileType

    file_size = 16 * CHUNK
    link = SharedLink(file_size)
    pool = [link.session() for _ in range(3)]
    for session in pool[1:]:
        await session.stop()
    media_window(pool[0].auth_key, 2).size = 3
    client = link_client(monkeypatch, link, pool)

    got = 0
    async for chunk in client.get_file(
        FileId(file_type=FileType.DOCUMENT, dc_id=2, media_id=1, access_hash=1), file_size
    ):
        got += len(chunk)

    assert got == file_size


async def test_a_cdn_connection_leaves_no_window_behind():
    session = Session(
        DummyClient(), 203, b"\x07" * 256, False, is_media=True, is_cdn=True, crypto_executor=None
    )
    session.connection = ClosingConnection()

    await session.recv_worker()

    assert (session.auth_key, 203) not in session_mod._media_windows, (
        "a CDN key is minted per download; a window per key grows without bound"
    )
