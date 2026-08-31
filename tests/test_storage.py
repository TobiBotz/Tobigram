import asyncio
import logging
import struct
import threading
import time
import zlib
from unittest import mock

import pytest

import pyrogram
import pyrogram.client
from pyrogram.utils import ainput
from pyrogram.storage import Storage, SQLiteStorage
from pyrogram.storage.storage import WZ_PREFIX
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
        assert len(s) == 438
        assert s.startswith("WZ_")

        await storage.close()

    @pytest.mark.asyncio
    async def test_export_session_string_survives_an_ipv6_address(self):
        address = "2001:067c:04e8:f004:0000:0000:0000:000b"

        storage = MemoryStorage(":memory:")
        await storage.open()
        await storage.dc_id(4)
        await storage.api_id(12345)
        await storage.test_mode(False)
        await storage.auth_key(b"\x11" * 256)
        await storage.user_id(999)
        await storage.is_bot(False)
        await storage.date(0)
        await storage.server_address(address)
        await storage.port(443)

        s = await storage.export_session_string()
        await storage.close()

        imported = MemoryStorage(":memory:")
        await imported.open()
        await imported.load_session_string(s)

        assert await imported.server_address() == address

        await imported.close()

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


AUTH_KEY = b"K" * 256
USER_ID = 8305084482
NEWLINE = chr(10)


def packed_v2():
    return struct.pack(
        Storage.SESSION_STRING_FORMAT_V2,
        2, 2, 1234, False, AUTH_KEY, USER_ID, True, 0, bytes(16)
    )


def session_string(kind):
    """Every wire format wzgram has ever exported."""
    if kind == "v2_crc":
        body = packed_v2()
        return Storage._encode(body + struct.pack("<I", zlib.crc32(body)))

    if kind == "v2":
        return Storage._encode(packed_v2())

    if kind == "legacy_267":
        return Storage._encode(struct.pack(">B?256sQ?", 2, False, AUTH_KEY, USER_ID, True))

    if kind == "legacy_271":
        return Storage._encode(
            struct.pack(">BI?256sQ?", 2, 1234, False, AUTH_KEY, USER_ID, True)
        )

    raise AssertionError(kind)


class TestSessionStringDecoding:
    """A session string wzgram itself exported has to keep working.

    The prefixed branch used to try only the CRC format and then raise, so every
    string exported before the CRC was added - all of which carry the prefix -
    reported itself as corrupted. Stripping a stray character out of the body
    raised the same flag, so a legacy string that picked up a newline from a
    database column or an env var was unreadable too.
    """

    @pytest.mark.parametrize("kind", ["v2_crc", "v2", "legacy_267", "legacy_271"])
    @pytest.mark.parametrize("wrap", ["bare", "prefixed", "stray_character"])
    def test_every_exported_format_decodes(self, kind, wrap):
        body = session_string(kind)
        candidate = {
            "bare": body,
            "prefixed": WZ_PREFIX + body,
            "stray_character": body[:40] + NEWLINE + body[40:],
        }[wrap]

        assert Storage._decode_session_string(candidate)["user_id"] == USER_ID

    def test_a_truncated_string_is_still_refused(self):
        with pytest.raises(ValueError, match="corrupted"):
            Storage._decode_session_string(WZ_PREFIX + session_string("v2_crc")[:-8])

    def test_a_repair_is_only_trusted_when_a_checksum_confirms_it(self):
        """Repair guesses characters, so only the CRC can vouch for the result.

        Accepting a repaired string with no checksum would hand back an auth key
        assembled from a guess.
        """
        with pytest.raises(ValueError, match="corrupted"):
            Storage._decode_session_string(session_string("v2")[:-8])

    def test_a_dropped_character_is_repaired_when_the_checksum_agrees(self):
        body = session_string("v2_crc")

        assert Storage._decode_session_string(body[:-1])["user_id"] == USER_ID

    def test_an_empty_string_says_so(self):
        with pytest.raises(ValueError, match="empty"):
            Storage._decode_session_string("   ")


class TestSessionStringLoading:
    """A session string has to bring its datacenter address with it.

    Resolving the address was nested inside `if data["api_id"] is not None`, so
    a legacy string - which carries no api_id - kept whatever address create()
    had seeded, which is DC 2's. A DC 4 session then offered a DC 4 auth key to
    DC 2. A v2 string exported before the address was known packs sixteen NUL
    bytes, which is not None, so it wrote an empty address and port 0.
    """

    @pytest.mark.parametrize(
        "kind,expected_api_id",
        [("legacy_dc4", None), ("v2_dc4", 1234), ("v2_dc4_blank_address", 1234)],
    )
    async def test_the_address_always_matches_the_datacenter(self, kind, expected_api_id):
        if kind == "legacy_dc4":
            string = Storage._encode(
                struct.pack(">B?256sQ?", 4, False, AUTH_KEY, USER_ID, True)
            )
        else:
            address = (
                bytes(16) if kind == "v2_dc4_blank_address"
                else PROD[4].encode("ascii").ljust(16, bytes(1))[:16]
            )
            port = 0 if kind == "v2_dc4_blank_address" else 443
            body = struct.pack(
                Storage.SESSION_STRING_FORMAT_V2,
                2, 4, 1234, False, AUTH_KEY, USER_ID, True, port, address
            )
            string = Storage._encode(body + struct.pack("<I", zlib.crc32(body)))

        storage = MemoryStorage("dc4", session_string=string)
        await storage.open()

        assert await storage.dc_id() == 4
        assert await storage.server_address() == PROD[4], (
            "the stored address must belong to the session's own datacenter"
        )
        assert await storage.port() == 443
        assert await storage.api_id() == expected_api_id

    async def test_a_session_with_no_api_id_can_still_be_re_exported(self):
        """The legacy warning asks the user to re-export; that has to be possible.

        api_id was in the required-fields check, so the one format that cannot
        carry an api_id was also the one that could never be re-exported.
        """
        string = Storage._encode(
            struct.pack(">B?256sQ?", 2, False, AUTH_KEY, USER_ID, True)
        )
        storage = MemoryStorage("legacy", session_string=string)
        await storage.open()

        exported = await storage.export_session_string()
        again = Storage._decode_session_string(exported)

        assert again["user_id"] == USER_ID
        assert again["auth_key"] == AUTH_KEY
        assert again["dc_id"] == 2
        assert again["api_id"] == 0, (
            "an unknown api_id round trips as 0, which load_session treats as "
            "absent and backfills from the Client"
        )

    async def test_a_still_incomplete_session_is_refused(self):
        storage = MemoryStorage("empty")
        await storage.open()

        with pytest.raises(ValueError, match="required fields are missing"):
            await storage.export_session_string()


class TestApiIdMigrationPrompt:
    async def test_a_headless_host_is_told_what_to_do_instead_of_spinning(self, monkeypatch):
        """load_session prompts for a missing api_id in a bare `while True`.

        With no terminal, input() raises EOFError on every pass, the broad
        except printed it and looped again: 3123 passes in 1.5s, each spawning a
        thread and writing to stdout, forever.
        """
        string = Storage._encode(
            struct.pack(">B?256sQ?", 2, False, AUTH_KEY, USER_ID, True)
        )
        app = pyrogram.Client(
            "prompt", session_string=string, api_id=None, api_hash=None, in_memory=True
        )
        await app.storage.open()

        asked = []

        async def no_terminal(prompt="", **kwargs):
            asked.append(prompt)

            if len(asked) > 5:
                raise AssertionError("still spinning on a host with no terminal")

            raise EOFError("EOF when reading a line")

        monkeypatch.setattr(pyrogram.client, "ainput", no_terminal)

        with pytest.raises(AttributeError, match="Pass api_id"):
            await asyncio.wait_for(app.load_session(), 10)

        assert len(asked) == 1


class TestPrompts:
    async def test_a_cancelled_prompt_does_not_wedge_the_loop(self):
        """ainput used a `with ThreadPoolExecutor(1)`, whose exit joins the thread.

        A thread parked in input() never returns, so timing out or cancelling a
        prompt hung on executor shutdown instead of unwinding.
        """
        started = threading.Event()
        release = threading.Event()

        def blocking(_prompt):
            started.set()
            release.wait(30)
            return "late"

        with mock.patch("builtins.input", blocking):
            task = asyncio.ensure_future(ainput("prompt: "))

            await asyncio.get_running_loop().run_in_executor(None, started.wait, 10)

            task.cancel()
            start = time.monotonic()

            try:
                with pytest.raises(asyncio.CancelledError):
                    await task
            finally:
                release.set()

            assert time.monotonic() - start < 5, (
                "cancelling the prompt waited on the parked thread instead of "
                "unwinding, so a timed-out prompt wedges the event loop"
            )
