"""HybridStorage: reads stay local, writes reach the backend, and neither a slow
backend nor a dead one is allowed to become the client's problem.

Each case here fails with its fix reverted - the drop-priority test in
particular, which is the difference between losing a peer lookup and losing the
login.
"""

import asyncio

import pytest

from pyrogram.storage import HybridStorage
from pyrogram.storage.hybrid_storage import PEER_WRITE, SESSION_WRITE

from .test_storage_contract import FakeRemote


async def drained(storage: HybridStorage) -> None:
    await asyncio.wait_for(storage._queue.join(), timeout=5)


@pytest.fixture
async def hybrid(tmp_path):
    backend = FakeRemote("hybrid")
    storage = HybridStorage("hybrid", backend=backend, workdir=tmp_path, flush_timeout=1)

    await storage.open()

    try:
        yield storage, backend
    finally:
        await storage.close()


class TestReadsStayLocal:
    async def test_peer_read_never_touches_a_broken_backend(self, hybrid):
        storage, backend = hybrid

        await storage.update_peers([(123, 456, "user", None)])
        await drained(storage)

        backend.fail_reads = True

        peer = await storage.get_peer_by_id(123)

        assert peer.user_id == 123

    async def test_session_read_never_touches_a_broken_backend(self, hybrid):
        storage, backend = hybrid

        await storage.dc_id(4)
        backend.fail_reads = True

        assert await storage.dc_id() == 4

    async def test_close_is_bounded_when_the_backend_is_gone(self, tmp_path):
        """A dead backend must not hold shutdown for twice the timeout."""
        backend = FakeRemote("gone")
        storage = HybridStorage("gone", backend=backend, workdir=tmp_path, flush_timeout=0.5)
        storage.RETRY_DELAY = 0.01

        await storage.open()
        backend.fail_writes = True
        await storage.update_peers([(1, 11, "user", None)])

        started = asyncio.get_running_loop().time()
        await storage.close()
        elapsed = asyncio.get_running_loop().time() - started

        assert elapsed < 1.5, f"close() took {elapsed:.1f}s for a 0.5s budget"

    async def test_warm_copies_the_backend_into_the_cache(self, tmp_path):
        backend = FakeRemote("warm")
        await backend.open()
        await backend.dc_id(5)
        await backend.auth_key(b"k" * 256)
        await backend.update_state((7, 100, 0, 1600000000, 3))
        await backend.update_peers([(123, 456, "user", None)])
        await backend.close()

        storage = HybridStorage("warm", backend=backend, workdir=tmp_path)
        await storage.open()

        try:
            backend.fail_reads = True

            assert await storage.dc_id() == 5
            assert await storage.auth_key() == b"k" * 256
            assert [tuple(s) for s in await storage.update_state()] == [
                (7, 100, 0, 1600000000, 3)
            ]
            assert (await storage.get_peer_by_id(123)).access_hash == 456
        finally:
            await storage.close()

    async def test_peers_are_warmed_on_open(self, tmp_path):
        """A client coming up on a new host must not pay an RPC per peer to
        rebuild a cache the backend already holds."""
        backend = FakeRemote("warmpeers")
        await backend.open()
        await backend.update_peers([(i, i * 10, "user", None) for i in range(1, 21)])
        await backend.close()

        storage = HybridStorage("warmpeers", backend=backend, workdir=tmp_path, flush_timeout=1)
        await storage.open()

        try:
            backend.fail_reads = True

            for peer_id in range(1, 21):
                assert (await storage.get_peer_by_id(peer_id)).access_hash == peer_id * 10
        finally:
            await storage.close()

    async def test_warm_limit_is_respected(self, tmp_path):
        backend = FakeRemote("limited")
        await backend.open()
        await backend.update_peers([(i, i * 10, "user", None) for i in range(1, 21)])
        await backend.close()

        storage = HybridStorage(
            "limited", backend=backend, workdir=tmp_path, warm_peers=5, flush_timeout=1
        )
        await storage.open()

        try:
            backend.fail_reads = True

            with pytest.raises(ConnectionError):
                for peer_id in range(1, 21):
                    await storage.get_peer_by_id(peer_id)
        finally:
            await storage.close()

    async def test_a_backend_that_cannot_enumerate_still_opens(self, tmp_path):
        class NoExport(FakeRemote):
            async def _iter_peers(self, limit=None):
                return []

        backend = NoExport("noexport")
        storage = HybridStorage("noexport", backend=backend, workdir=tmp_path, flush_timeout=1)

        await storage.open()

        try:
            await storage.update_peers([(1, 11, "user", None)])
            assert (await storage.get_peer_by_id(1)).access_hash == 11
        finally:
            await storage.close()


class TestWritesReachTheBackend:
    async def test_peers_are_mirrored(self, hybrid):
        storage, backend = hybrid

        await storage.update_peers([(123, 456, "user", None)])
        await drained(storage)

        assert backend.peers[123][:3] == (123, 456, "user")

    async def test_session_attributes_are_mirrored(self, hybrid):
        storage, backend = hybrid

        await storage.auth_key(b"z" * 256)
        await storage.user_id(777000)
        await drained(storage)

        assert backend.session["auth_key"] == b"z" * 256
        assert backend.session["user_id"] == 777000

    async def test_update_state_is_mirrored_and_deletable(self, hybrid):
        storage, backend = hybrid

        await storage.update_state((1, 100, 0, 1600000000, 5))
        await drained(storage)
        assert 1 in backend.states

        await storage.update_state(1)
        await drained(storage)
        assert 1 not in backend.states

    async def test_close_flushes_what_is_queued(self, tmp_path):
        backend = FakeRemote("flush")
        storage = HybridStorage("flush", backend=backend, workdir=tmp_path, flush_timeout=2)

        await storage.open()
        await storage.update_peers([(1, 11, "user", None)])
        await storage.close()

        assert 1 in backend.peers


class TestDelete:
    async def test_a_queued_write_is_not_replayed_after_a_purge(self, tmp_path):
        class Slow(FakeRemote):
            async def _save_session(self, fields):
                await asyncio.sleep(0.2)
                return await super()._save_session(fields)

        backend = Slow("purge")
        storage = HybridStorage("purge", backend=backend, workdir=tmp_path, flush_timeout=1)

        await storage.open()
        await storage.auth_key(b"k" * 256)
        await asyncio.sleep(0)

        await storage.delete()

        assert backend.session is None

        await asyncio.sleep(0.5)

        assert backend.session is None, "a queued write put the session back after the purge"

        await storage.close()


class TestBackendFailures:
    async def test_write_failure_does_not_reach_the_caller(self, hybrid):
        storage, backend = hybrid

        storage.RETRY_DELAY = 0.01
        backend.fail_writes = True

        await storage.update_peers([(1, 11, "user", None)])
        await storage.auth_key(b"k" * 256)

        assert (await storage.get_peer_by_id(1)).user_id == 1

    async def test_writes_resume_after_the_backend_returns(self, tmp_path):
        backend = FakeRemote("retry")
        storage = HybridStorage("retry", backend=backend, workdir=tmp_path, flush_timeout=1)
        storage.RETRY_DELAY = 0.01

        await storage.open()

        try:
            backend.fail_writes = True
            await storage.update_peers([(1, 11, "user", None)])

            await asyncio.sleep(0.05)
            backend.fail_writes = False

            await asyncio.wait_for(storage._queue.join(), timeout=5)

            assert 1 in backend.peers
        finally:
            await storage.close()


class TestBackpressure:
    async def test_queue_is_bounded(self, tmp_path):
        backend = FakeRemote("bounded")
        storage = HybridStorage("bounded", backend=backend, workdir=tmp_path, queue_size=4)

        await storage.open()

        try:
            storage._writer.cancel()

            for peer_id in range(50):
                await storage.update_peers([(peer_id + 1, peer_id, "user", None)])

            assert storage._queue.qsize() <= 4
            assert storage.dropped_writes > 0
        finally:
            storage._closing = True
            await storage.local.close()
            await backend.close()

    async def test_session_writes_are_never_the_ones_dropped(self, tmp_path):
        """Losing a peer costs a lookup; losing an auth key costs the login."""
        backend = FakeRemote("priority")
        storage = HybridStorage("priority", backend=backend, workdir=tmp_path, queue_size=3)

        await storage.open()

        try:
            storage._writer.cancel()

            await storage.auth_key(b"k" * 256)

            for peer_id in range(20):
                await storage.update_peers([(peer_id + 1, peer_id, "user", None)])

            queued = list(storage._queue._queue)
            kinds = [kind for kind, _ in queued]

            assert SESSION_WRITE in kinds, "the session write was dropped under pressure"
            assert kinds.count(PEER_WRITE) < 20
        finally:
            storage._closing = True
            await storage.local.close()
            await backend.close()


class TestWriterTask:
    async def test_writer_task_is_strongly_referenced(self, hybrid):
        """The loop keeps only a weak reference to a task, so fire-and-forget work
        with no other referent can be collected mid-await and simply stop."""
        storage, _ = hybrid

        from pyrogram.utils import _background_tasks

        assert storage._writer in _background_tasks

    async def test_writer_stops_on_close(self, tmp_path):
        backend = FakeRemote("stop")
        storage = HybridStorage("stop", backend=backend, workdir=tmp_path, flush_timeout=2)

        await storage.open()
        writer = storage._writer
        await storage.close()

        assert writer.done()
        assert storage._writer is None
