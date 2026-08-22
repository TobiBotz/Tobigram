"""RemoteStorage's own rules: the caches, and what they are allowed to skip.

These are the invariants a hand-written engine gets wrong, so they are asserted
against the base class rather than against any particular backend.
"""

import time

import pytest

from pyrogram.storage import RemoteStorage
from pyrogram.storage.caching import PeerRowCache, SessionAttrCache

from .test_storage_contract import FakeRemote


class TestPeerCache:
    async def test_hit_never_reaches_the_backend(self):
        storage = FakeRemote()
        await storage.open()

        await storage.update_peers([(123, 456, "user", None)])
        reads = storage.reads

        await storage.get_peer_by_id(123)
        await storage.get_peer_by_id(123)

        assert storage.reads == reads, "a cached peer must not be fetched again"

        await storage.close()

    async def test_miss_falls_through_and_is_then_cached(self):
        storage = FakeRemote()
        await storage.open()

        storage.peers[999] = (999, 111, "user", None, int(time.time()))
        reads = storage.reads

        await storage.get_peer_by_id(999)
        assert storage.reads == reads + 1

        await storage.get_peer_by_id(999)
        assert storage.reads == reads + 1

        await storage.close()

    async def test_unchanged_peers_are_not_rewritten(self):
        """Every invoke feeds r.users and r.chats back through fetch_peers, so
        without this filter the same peers are rewritten on every single RPC."""
        storage = FakeRemote()
        await storage.open()

        batch = [(1, 11, "user", None), (2, 22, "user", None)]

        await storage.update_peers(batch)
        writes = storage.writes

        await storage.update_peers(batch)

        assert storage.writes == writes, "unchanged peers must not be written again"

        await storage.close()

    async def test_changed_access_hash_is_still_written(self):
        storage = FakeRemote()
        await storage.open()

        await storage.update_peers([(1, 11, "user", None)])
        writes = storage.writes

        await storage.update_peers([(1, 99, "user", None)])

        assert storage.writes == writes + 1
        assert storage.peers[1][1] == 99

        await storage.close()

    async def test_cache_is_bounded(self):
        cache = PeerRowCache(size=3)

        for peer_id in range(10):
            cache.remember((peer_id, peer_id, "user"))

        assert len(cache) == 3
        assert cache.get(9) is not None
        assert cache.get(0) is None

    async def test_cache_holds_rows_not_input_peers(self):
        """Callers hand InputPeers to the API and are free to mutate them, so a
        shared instance would be shared mutable state."""
        storage = FakeRemote()
        await storage.open()

        await storage.update_peers([(123, 456, "user", None)])

        first = await storage.get_peer_by_id(123)
        second = await storage.get_peer_by_id(123)

        assert first is not second
        first.access_hash = 0
        assert second.access_hash == 456

        await storage.close()


class TestUsernameTTL:
    async def test_expired_username_raises(self):
        storage = FakeRemote()
        await storage.open()

        await storage.update_peers([(123, 456, "user", None)])
        await storage.update_usernames([(123, ["alice"])])

        storage.touch_peer(123, int(time.time()) - RemoteStorage.USERNAME_TTL - 60)

        with pytest.raises(KeyError, match="expired"):
            await storage.get_peer_by_username("alice")

        await storage.close()

    async def test_fresh_username_resolves(self):
        storage = FakeRemote()
        await storage.open()

        await storage.update_peers([(123, 456, "user", None)])
        await storage.update_usernames([(123, ["alice"])])

        storage.touch_peer(123, int(time.time()) - 60)

        assert (await storage.get_peer_by_username("alice")).user_id == 123

        await storage.close()


class TestSessionAttrCache:
    async def test_attribute_read_once(self):
        storage = FakeRemote()
        await storage.open()

        reads = storage.reads

        await storage.dc_id()
        await storage.dc_id()
        await storage.dc_id()

        assert storage.reads == reads, "session attributes must be served from memory"

        await storage.close()

    def test_missing_and_none_are_different_states(self):
        cache = SessionAttrCache()

        assert "user_id" not in cache

        cache.remember("user_id", None)

        assert "user_id" in cache
        assert cache.get("user_id") is None

    async def test_write_updates_the_cache(self):
        storage = FakeRemote()
        await storage.open()

        await storage.auth_key(b"k" * 256)
        reads = storage.reads

        assert await storage.auth_key() == b"k" * 256
        assert storage.reads == reads

        await storage.close()


class TestLifecycle:
    async def test_open_seeds_a_default_session(self):
        storage = FakeRemote()
        await storage.open()

        assert storage.session is not None
        assert await storage.dc_id() == 2
        assert storage.stored_version == RemoteStorage.VERSION

        await storage.close()

    async def test_open_is_idempotent(self):
        storage = FakeRemote()
        await storage.open()
        await storage.open()

        assert storage.connected

        await storage.close()

    async def test_reads_after_close_are_refused(self):
        storage = FakeRemote()
        await storage.open()
        await storage.close()

        with pytest.raises(ConnectionError):
            await storage.dc_id()

    async def test_delete_keeps_peers_when_asked(self):
        storage = FakeRemote()
        await storage.open()

        await storage.update_peers([(1, 11, "user", None)])
        await storage.delete(remove_peers=False)

        assert storage.peers
        assert storage.session is None

        await storage.close()
