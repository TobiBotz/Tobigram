import logging

import pytest

from pyrogram.storage import Storage, SQLiteStorage
from pyrogram.storage import sqlite_storage
from pyrogram.storage.memory_storage import MemoryStorage
from pyrogram.storage.sqlite_storage import PROD


class TestStorageABC:
    def test_storage_is_abstract(self):
        with pytest.raises(TypeError):
            Storage()  # abstract – can't instantiate directly

    def test_storage_has_abstract_methods(self):
        methods = [
            "open", "save", "close", "delete",
            "update_peers", "update_usernames", "update_state",
            "get_peer_by_id", "get_peer_by_username",
            "get_peer_by_phone_number",
            "dc_id", "api_id", "server_address", "port",
            "test_mode", "auth_key", "date", "user_id", "is_bot",
        ]
        for m in methods:
            assert hasattr(Storage, m), f"Storage missing abstract method: {m}"

    def test_storage_constants(self):
        assert Storage.V2_PACKED_SIZE == 290
        assert Storage.V2_CRC_PACKED_SIZE == 294
        assert Storage.SESSION_STRING_FORMAT_V2 == ">BBI?256sQ?H16s"


class TestMemoryStorage:
    def test_create_minimal(self):
        storage = MemoryStorage(":memory:")
        assert storage.name == ":memory:"
        assert storage.session_string is None

    def test_create_with_session_string(self):
        storage = MemoryStorage(":memory:", session_string="dummy")
        assert storage.session_string == "dummy"

    def test_open_creates_db(self):
        storage = MemoryStorage(":memory:")
        # Before open, conn should be None
        assert storage.conn is None

    @pytest.mark.asyncio
    async def test_open_and_set_values(self):
        storage = MemoryStorage(":memory:")
        await storage.open()
        assert storage.conn is not None

        # Set values via the property-style setters
        await storage.dc_id(2)
        await storage.api_id(12345)
        await storage.test_mode(True)
        await storage.user_id(67890)
        await storage.is_bot(False)
        await storage.auth_key(b"\x00" * 256)
        await storage.date(1000)

        # Read them back (SQLite stores bools as 0/1)
        assert await storage.dc_id() == 2
        assert await storage.api_id() == 12345
        assert await storage.test_mode() == 1
        assert await storage.user_id() == 67890
        assert await storage.is_bot() == 0
        assert await storage.auth_key() == b"\x00" * 256
        assert await storage.date() == 1000

        await storage.save()
        await storage.close()

    @pytest.mark.asyncio
    async def test_open_twice(self):
        storage = MemoryStorage(":memory:")
        await storage.open()
        await storage.open()  # should not raise
        await storage.close()

    @pytest.mark.asyncio
    async def test_delete_noop(self):
        storage = MemoryStorage(":memory:")
        await storage.open()
        await storage.delete()  # should not raise
        await storage.close()

    @pytest.mark.asyncio
    async def test_update_peers(self):
        storage = MemoryStorage(":memory:")
        await storage.open()
        await storage.update_peers([(123, 456, "user", "+1234567890")])

        peer = await storage.get_peer_by_id(123)
        assert peer is not None
        assert peer.user_id == 123

        await storage.close()

    @pytest.mark.asyncio
    async def test_get_peer_by_username(self):
        storage = MemoryStorage(":memory:")
        await storage.open()
        await storage.update_peers([(789, 101112, "user", "")])
        await storage.update_usernames([(789, ["testuser"])])

        peer = await storage.get_peer_by_username("testuser")
        assert peer is not None
        assert peer.user_id == 789

        await storage.close()

    @pytest.mark.asyncio
    async def test_get_peer_by_phone_number(self):
        storage = MemoryStorage(":memory:")
        await storage.open()
        await storage.update_peers([(111, 222, "user", "+111222333")])

        peer = await storage.get_peer_by_phone_number("+111222333")
        assert peer is not None
        assert peer.user_id == 111

        await storage.close()

    @pytest.mark.asyncio
    async def test_peer_not_found_raises(self):
        storage = MemoryStorage(":memory:")
        await storage.open()

        with pytest.raises(KeyError):
            await storage.get_peer_by_id(999999)

        await storage.close()

    @pytest.mark.asyncio
    async def test_update_state(self):
        storage = MemoryStorage(":memory:")
        await storage.open()
        state = (0, 1, 2, 3, 4)
        await storage.update_state(state)

        # read back (returns list of tuples)
        state2 = await storage.update_state()
        assert state2 == [state]

        await storage.close()

    @pytest.mark.asyncio
    async def test_export_session_string(self):
        storage = MemoryStorage(":memory:")
        await storage.open()
        await storage.dc_id(2)
        await storage.api_id(12345)
        await storage.test_mode(False)
        await storage.auth_key(b"\x11" * 256)
        await storage.user_id(999)
        await storage.is_bot(False)
        await storage.date(0)
        await storage.server_address("149.154.167.50")
        await storage.port(443)

        s = await storage.export_session_string()
        assert isinstance(s, str)
        assert len(s) == 395
        assert s.startswith("WZ_")

        await storage.close()

    @pytest.mark.asyncio
    async def test_server_address_and_port(self):
        storage = MemoryStorage(":memory:")
        await storage.open()
        await storage.server_address("149.154.167.50")
        await storage.port(443)
        assert await storage.server_address() == "149.154.167.50"
        assert await storage.port() == 443
        await storage.close()

    def test_is_subclass_of_sqlite_storage(self):
        assert issubclass(MemoryStorage, SQLiteStorage)


class TestSQLiteStorageMigration:
    @pytest.mark.asyncio
    async def test_stale_address_is_reset_to_match_dc_id(self, tmp_path):
        storage = SQLiteStorage("stale", workdir=tmp_path)
        await storage.open()
        await storage.test_mode(False)
        await storage.auth_key(b"k" * 256)
        await storage.server_address("149.154.167.51")
        await storage.port(443)
        await storage.dc_id(4)
        await storage.version(7)
        await storage.close()

        storage = SQLiteStorage("stale", workdir=tmp_path)
        await storage.open()
        try:
            assert await storage.dc_id() == 4
            assert await storage.server_address() == PROD[4]
            assert await storage.port() == 443
            assert await storage.version() == SQLiteStorage.VERSION
        finally:
            await storage.close()

    @pytest.mark.asyncio
    async def test_migration_skips_an_unknown_dc(self, tmp_path):
        storage = SQLiteStorage("unknown", workdir=tmp_path)
        await storage.open()
        await storage.test_mode(False)
        await storage.server_address("10.0.0.1")
        await storage.dc_id(99)
        await storage.version(7)
        await storage.close()

        storage = SQLiteStorage("unknown", workdir=tmp_path)
        await storage.open()
        try:
            assert await storage.server_address() == "10.0.0.1"
        finally:
            await storage.close()

    @pytest.mark.asyncio
    async def test_migration_from_v6_handles_a_dc_missing_from_the_address_table(self, tmp_path):
        storage = SQLiteStorage("v6", workdir=tmp_path)
        await storage.open()
        await storage.test_mode(True)
        await storage.dc_id(4)
        await storage.conn.execute("ALTER TABLE sessions DROP COLUMN server_address;")
        await storage.conn.execute("ALTER TABLE sessions DROP COLUMN port;")
        await storage.version(6)
        await storage.close()

        storage = SQLiteStorage("v6", workdir=tmp_path)
        await storage.open()
        try:
            assert await storage.version() == SQLiteStorage.VERSION
            assert await storage.server_address() is None
            assert await storage.port() is None
        finally:
            await storage.close()


class TestSQLiteStorageLocking:
    @pytest.mark.asyncio
    async def test_a_platform_without_flock_does_not_warn_about_other_clients(
        self, tmp_path, monkeypatch, caplog
    ):
        monkeypatch.setattr(sqlite_storage, "fcntl", None)

        storage = SQLiteStorage("nolock", workdir=tmp_path)
        await storage.open()
        await storage.close()

        with caplog.at_level(logging.WARNING, logger=sqlite_storage.log.name):
            storage = SQLiteStorage("nolock", workdir=tmp_path)
            await storage.open()
            await storage.close()

        assert caplog.records == []


class TestSQLiteStoragePersistence:
    @pytest.mark.asyncio
    async def test_writes_survive_close_without_save(self, tmp_path):
        storage = SQLiteStorage("persist", workdir=tmp_path)
        await storage.open()
        await storage.update_peers([(123, 456, "user", "+1234567890")])
        await storage.update_usernames([(123, ["bob"])])
        await storage.update_state((1, 2, 3, 4, 5))
        await storage.close()

        storage = SQLiteStorage("persist", workdir=tmp_path)
        await storage.open()
        try:
            assert (await storage.get_peer_by_id(123)).user_id == 123
            assert (await storage.get_peer_by_username("bob")).user_id == 123
            assert (await storage.get_peer_by_phone_number("+1234567890")).user_id == 123
            assert await storage.update_state() == [(1, 2, 3, 4, 5)]
        finally:
            await storage.close()
