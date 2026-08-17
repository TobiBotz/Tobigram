import asyncio
import time
import tracemalloc
from types import SimpleNamespace

import pyrogram
from pyrogram import raw
from pyrogram.file_id import FileId, FileType
from pyrogram.session.session import Session

CHUNK = 1024 * 1024
UPLOAD_PART = 512 * 1024


def payload_for(offset, size):
    return bytes([(offset // CHUNK) & 0xFF]) * size


def expected_byte(index):
    return index & 0xFF


class SessionOwner:
    name = "e2e"
    app_version = "1.0"
    device_model = "Test"
    system_version = "Linux"
    lang_code = "en"
    loop = None
    is_media = False
    proxy = None
    ipv6 = False
    dc_id = 2
    session = None
    disconnect_handler = None

    class storage:
        conn = object()

        @staticmethod
        async def api_id():
            return 1

        @staticmethod
        async def open():
            pass

    async def handle_updates(self, body):
        pass


class FakeDC:
    def __init__(self, file_size, step=0.002):
        self.file_size = file_size
        self.step = step

        self.inflight = 0
        self.peak_inflight = 0
        self.peak_per_session = {}
        self.served = 0
        self.timeouts = 0

    def session(self, client=None, is_media=True, dc_id=2):
        session = Session(
            client or SessionOwner(), dc_id, b"\x00" * 256, False,
            is_media=is_media, crypto_executor=None
        )
        session.is_started.set()
        session.send = self._send_for(session)
        return session

    def pool(self, size=3, client=None):
        return [self.session(client) for _ in range(size)]

    def _send_for(self, session):
        key = id(session)
        self.peak_per_session.setdefault(key, 0)

        async def send(query, wait_response=True, timeout=None, retry=0):
            self.inflight += 1
            self.peak_per_session[key] += 1
            self.peak_inflight = max(self.peak_inflight, self.inflight)
            session.last_packet_received = time.monotonic()

            try:
                needed = self.step * self.inflight
                await asyncio.sleep(min(needed, timeout) if timeout else needed)
                session.last_packet_received = time.monotonic()

                if timeout is not None and needed > timeout:
                    self.timeouts += 1
                    raise TimeoutError("Request timed out")

                return self._answer(query)
            finally:
                self.inflight -= 1
                self.peak_per_session[key] -= 1

        return send

    def peak_on_one_connection(self):
        return max(self._peaks) if self._peaks else 0

    def _answer(self, query):
        inner = getattr(query, "query", query)

        if isinstance(inner, raw.functions.upload.GetFile):
            self.served += 1
            remaining = max(0, self.file_size - inner.offset)
            return raw.types.upload.File(
                type=raw.types.storage.FilePartial(),
                mtime=0,
                bytes=payload_for(inner.offset, min(CHUNK, remaining)),
            )

        if isinstance(
            inner,
            (raw.functions.upload.SaveBigFilePart, raw.functions.upload.SaveFilePart),
        ):
            self.served += 1
            return True

        return True


class TrackingDC(FakeDC):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.high_water = {}

    def _send_for(self, session):
        key = id(session)
        self.high_water.setdefault(key, 0)
        live = {"n": 0}
        inner_send = super()._send_for(session)

        async def send(query, **kwargs):
            live["n"] += 1
            self.high_water[key] = max(self.high_water[key], live["n"])
            try:
                return await inner_send(query, **kwargs)
            finally:
                live["n"] -= 1

        return send

    @property
    def worst_connection(self):
        return max(self.high_water.values()) if self.high_water else 0


def make_client(dc, name="e2e", pool=None, sessions=3, premium=False, bot=False):
    client = pyrogram.Client(name, api_id=1, api_hash="x", in_memory=True)
    client.me = SimpleNamespace(is_bot=bot, is_premium=premium)

    pool = pool if pool is not None else dc.pool(sessions, client)

    async def get_session(*args, **kwargs):
        return pool[0]

    async def get_pool(dc_id, n):
        return pool

    client.get_session = get_session
    client._get_media_session_pool = get_pool
    client.media_pool = pool
    return client


def document(dc_id=2):
    return FileId(file_type=FileType.DOCUMENT, dc_id=dc_id, media_id=1, access_hash=1)


class Measured:
    __slots__ = ("peak_bytes", "wall", "dc")

    def __init__(self, peak_bytes, wall, dc):
        self.peak_bytes = peak_bytes
        self.wall = wall
        self.dc = dc

    @property
    def peak_mib(self):
        return self.peak_bytes / CHUNK

    def __repr__(self):
        return (
            f"peak={self.peak_mib:.1f} MiB wall={self.wall:.2f}s "
            f"inflight<={self.dc.peak_inflight} timeouts={self.dc.timeouts} "
            f"parts={self.dc.served}"
        )


async def measure(coro_factory, dc):
    tracemalloc.start()
    tracemalloc.reset_peak()
    started = time.monotonic()
    try:
        await coro_factory()
    finally:
        _current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
    return Measured(peak, time.monotonic() - started, dc)


async def stream_all(client, file_size, verify=False):
    index = 0
    total = 0
    async for chunk in client.get_file(document(), file_size):
        if verify and chunk:
            assert set(chunk) == {expected_byte(index)}, (
                f"chunk {index} arrived out of order or corrupted"
            )
        index += 1
        total += len(chunk)
    return total


async def download_to(client, file_size, path):
    with open(path, "w+b") as handle:
        handle.truncate(file_size)
        async for _ in client.get_file(document(), file_size, _write_file=handle):
            pass
    return path
