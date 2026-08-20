"""Where a busy client actually spends its time.

    uv run python tests/benchmarks/bench_hot_path.py

Every number here is a thread hand-off in disguise: aiosqlite runs each
statement on its own thread, and the crypto pool is another. A hand-off costs a
flat ~110us on this machine, which is two orders of magnitude more than the work
being handed off for anything smaller than a transfer part.
"""

import asyncio
import tempfile
import time
from pathlib import Path
from types import SimpleNamespace

from pyrogram import raw
from pyrogram.session.session import Session
from pyrogram.storage import SQLiteStorage


class DummyClient:
    name = "bench"
    app_version = "1"
    device_model = "T"
    system_version = "L"
    lang_code = "en"
    proxy = None
    ipv6 = False
    session = None
    disconnect_handler = None


class NullConnection:
    def __init__(self):
        self.protocol = SimpleNamespace(crypto_executor=None)

    async def send(self, payload):
        pass

    async def close(self):
        pass


async def bench(label, fn, n):
    await fn()

    started = time.perf_counter()

    for i in range(n):
        await fn(i)

    elapsed = time.perf_counter() - started

    print(f"{label:<46} {elapsed / n * 1e6:9.1f} us/op {n / elapsed:10.0f} op/s")


async def main():
    session = Session(DummyClient(), 2, b"\x00" * 256, False, crypto_executor=None)
    session.connection = NullConnection()
    ping = raw.functions.Ping(ping_id=0)

    async def send(i=0):
        await session.send(ping, wait_response=False)

    for threshold, label in ((Session.INLINE_CRYPTO_MAX, "inline"), (0, "pool")):
        Session.INLINE_CRYPTO_MAX = threshold
        await bench(f"Session.send ping [{label}]", send, 3000)

    Session.INLINE_CRYPTO_MAX = 32 * 1024

    storage = SQLiteStorage("bench", Path(tempfile.mkdtemp()))
    await storage.open()
    await storage.update_peers([(1000 + i, 42 + i, "user", None) for i in range(50)])

    async def get_peer(i=0):
        await storage.get_peer_by_id(1000 + (i % 50))

    async def known_peers(i=0):
        await storage.update_peers([(1000 + j, 42 + j, "user", None) for j in range(20)])

    async def new_peer(i=0):
        await storage.update_peers([(500000 + i, 7, "user", None)])

    async def state(i=0):
        await storage.update_state((0, i, None, 1700000000, 1))

    await bench("storage.get_peer_by_id (cached)", get_peer, 3000)
    await bench("storage.update_peers x20 (unchanged)", known_peers, 3000)
    await bench("storage.update_peers (new peer)", new_peer, 1000)
    await bench("storage.update_state", state, 1000)

    await storage.close()


if __name__ == "__main__":
    asyncio.run(main())
