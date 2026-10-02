import ast
import asyncio
import sys
import time
from pathlib import Path

import pytest

import pyrogram
import pyrogram.session.session as session_mod
from pyrogram import raw
from pyrogram.connection import Connection
from pyrogram.connection.transport import TCPAbridged
from pyrogram.errors import AuthKeyUnregistered
from pyrogram.session.internals import msg_id as msg_id_mod, MsgId
from pyrogram.session.session import Session, _serialize_file_part


class DummyClient:
    name = "regress"
    app_version = "1.0"
    device_model = "Test"
    system_version = "Linux"
    lang_code = "en"
    loop = None
    is_media = False
    proxy = None
    ipv6 = False
    protocol_factory = TCPAbridged
    connection_factory = Connection
    init_connection_params = None
    dc_id = 2
    session = None
    connect_handler = None
    disconnect_handler = None

    class storage:
        conn = object()

        @staticmethod
        async def api_id():
            return 1

        @staticmethod
        async def open():
            pass


class _AuthFailThenUnreg:
    kills_with_unregistered_on = 0
    attempts = 0

    def __init__(self, *args, **kwargs):
        _AuthFailThenUnreg.attempts += 1

    async def connect(self):
        if self.attempts == 1:
            raise OSError("transient socket failure")
        raise AuthKeyUnregistered(401, "AUTH_KEY_UNREGISTERED")

    async def close(self):
        pass


class _AlwaysFails:
    attempts = 0

    def __init__(self, *args, **kwargs):
        _AlwaysFails.attempts += 1

    async def connect(self):
        raise OSError("persistent outage")

    async def close(self):
        pass


@pytest.fixture
def session_factory():
    return lambda: Session(
        DummyClient(),
        1,
        b"\x00" * 256,
        False,
        is_media=False,
        crypto_executor=None,
    )


async def test_fatal_auth_after_transient_retry_propagates(monkeypatch, session_factory):
    _AuthFailThenUnreg.attempts = 0
    monkeypatch.setattr(DummyClient, "connection_factory", _AuthFailThenUnreg)

    started = asyncio.get_event_loop().time()
    with pytest.raises(AuthKeyUnregistered):
        await asyncio.wait_for(session_factory().start(), timeout=5)

    elapsed = asyncio.get_event_loop().time() - started
    assert _AuthFailThenUnreg.attempts == 2, (
        f"expected transient OSError then fatal auth, got {_AuthFailThenUnreg.attempts} attempts"
    )
    assert elapsed < 4, f"fatal error should propagate fast, took {elapsed:.1f}s"


async def test_bounded_start_raises_instead_of_looping(monkeypatch, session_factory):
    _AlwaysFails.attempts = 0
    monkeypatch.setattr(DummyClient, "connection_factory", _AlwaysFails)

    started = asyncio.get_event_loop().time()
    with pytest.raises(OSError):
        await asyncio.wait_for(session_factory().start(max_attempts=2), timeout=5)

    elapsed = asyncio.get_event_loop().time() - started
    assert _AlwaysFails.attempts == 2, (
        f"expected start to stop after max_attempts, got {_AlwaysFails.attempts} attempts"
    )
    assert elapsed < 4, f"max_attempts should cap retries, took {elapsed:.1f}s"


class _BlackHoleThenHealthy:
    attempts = 0

    def __init__(self, *args, **kwargs):
        _BlackHoleThenHealthy.attempts += 1
        self.attempt = _BlackHoleThenHealthy.attempts
        self.protocol = type("P", (), {"crypto_executor": None})()
        self.queue = asyncio.Queue()

    async def connect(self):
        pass

    async def close(self):
        pass

    async def send(self, payload):
        if self.attempt >= 2:
            self.queue.put_nowait(b"reply")

    async def recv(self):
        return await self.queue.get()


async def test_start_retry_still_dispatches_packets(monkeypatch, session_factory):
    _BlackHoleThenHealthy.attempts = 0
    monkeypatch.setattr(DummyClient, "connection_factory", _BlackHoleThenHealthy)

    s = session_factory()
    s.is_media = True
    s.is_cdn = True
    handled = []

    async def fake_handle_packet(packet):
        handled.append(packet)
        for result in list(s.results.values()):
            result.value = object()
            result.event.set()

    monkeypatch.setattr(s, "handle_packet", fake_handle_packet)
    monkeypatch.setattr(s.loop, "run_in_executor", lambda ex, fn, *a: _packed())

    await asyncio.wait_for(s.start(max_attempts=4), timeout=30)

    assert _BlackHoleThenHealthy.attempts == 2, (
        f"a healthy second attempt must succeed, took {_BlackHoleThenHealthy.attempts}"
    )
    assert handled, "packets on a retried attempt must reach handle_packet"
    assert not s._stopping, "_stopping must be cleared for each start attempt"

    await s.stop()


async def _packed():
    return b"packed"


async def test_send_timeout_normalises_error_and_frees_result(monkeypatch, session_factory):
    s = session_factory()

    async def never_completes(payload):
        await asyncio.sleep(30)

    s.connection = type(
        "C",
        (),
        {
            "protocol": type("P", (), {"crypto_executor": None})(),
            "send": staticmethod(never_completes),
        },
    )()
    monkeypatch.setattr(s.loop, "run_in_executor", lambda ex, fn, *a: _packed())

    with pytest.raises(TimeoutError, match="send timed out"):
        await s.send(raw.functions.Ping(ping_id=0), timeout=0.05)

    assert not s.results, f"a timed-out send must release its result slot, got {s.results}"


class _OutageConn:
    outage = False

    def __init__(self, *args, **kwargs):
        self.protocol = type("P", (), {"crypto_executor": None})()
        self.queue = asyncio.Queue()

    async def connect(self):
        if _OutageConn.outage:
            raise OSError("no route to host")

    async def close(self):
        pass

    async def send(self, payload):
        if _OutageConn.outage:
            raise OSError("broken pipe")
        self.queue.put_nowait(b"reply")

    async def recv(self):
        while True:
            if _OutageConn.outage:
                return None
            try:
                return self.queue.get_nowait()
            except asyncio.QueueEmpty:
                await asyncio.sleep(0.01)


async def _wait_until(predicate, timeout=10):
    for _ in range(int(timeout / 0.05)):
        if predicate():
            return True
        await asyncio.sleep(0.05)
    return predicate()


async def test_dead_session_rearms_when_network_returns(monkeypatch):
    monkeypatch.setattr(DummyClient, "connection_factory", _OutageConn)
    monkeypatch.setattr(Session, "MAX_RETRIES", 2)
    monkeypatch.setattr(_OutageConn, "outage", False)

    s = Session(DummyClient(), 1, b"\x00" * 256, False, is_media=True, crypto_executor=None)
    s.is_cdn = True

    async def fake_handle_packet(packet):
        for result in list(s.results.values()):
            result.value = object()
            result.event.set()

    monkeypatch.setattr(s, "handle_packet", fake_handle_packet)
    monkeypatch.setattr(s.loop, "run_in_executor", lambda ex, fn, *a: _packed())

    await s.start(max_attempts=2)
    assert s.is_started.is_set()

    _OutageConn.outage = True
    assert await _wait_until(lambda: not s.is_started.is_set() and not s._start_active)
    assert isinstance(s._start_exc, OSError), (
        f"a restart driven by recv_worker must record why it failed, got {s._start_exc!r}"
    )

    _OutageConn.outage = False
    await asyncio.wait_for(
        s.invoke(raw.functions.Ping(ping_id=0), retries=3, timeout=1), timeout=15
    )
    assert s.is_started.is_set(), "invoke must re-arm a session nothing else will restart"

    await s.stop()


async def test_invoke_surfaces_real_start_failure(monkeypatch, session_factory):
    _AuthFailThenUnreg.attempts = 1
    monkeypatch.setattr(DummyClient, "connection_factory", _AuthFailThenUnreg)

    s = session_factory()

    started = asyncio.get_event_loop().time()
    with pytest.raises(AuthKeyUnregistered):
        await asyncio.wait_for(s.invoke(raw.functions.Ping(ping_id=0)), timeout=10)

    elapsed = asyncio.get_event_loop().time() - started
    assert elapsed < 4, f"a fatal start error must not be retried, took {elapsed:.1f}s"


async def test_invoke_waits_out_active_start_then_proceeds(monkeypatch, session_factory):
    s = session_factory()
    s._start_active = True
    s._start_completed.clear()
    assert not s.is_started.is_set()

    async def _finish_start():
        await asyncio.sleep(0.05)
        s.is_started.set()
        s._start_completed.set()

    task = asyncio.ensure_future(_finish_start())
    try:
        with pytest.raises(OSError, match="Connection is not established"):
            await asyncio.wait_for(
                s.invoke(raw.functions.Ping(ping_id=0), retries=1, timeout=1),
                timeout=2,
            )
    finally:
        await task


async def test_invoke_raises_bounded_start_error_after_active_finishes(
    monkeypatch, session_factory
):
    _AlwaysFails.attempts = 0
    monkeypatch.setattr(DummyClient, "connection_factory", _AlwaysFails)
    monkeypatch.setattr(Session, "MAX_RETRIES", 2)

    s = session_factory()
    s._start_active = True
    s._start_completed.clear()

    async def _fail_start():
        await asyncio.sleep(0.05)
        s._start_active = False
        s._start_completed.set()

    task = asyncio.ensure_future(_fail_start())
    try:
        with pytest.raises(OSError, match="persistent outage"):
            await asyncio.wait_for(
                s.invoke(raw.functions.Ping(ping_id=0), retries=2, timeout=1), timeout=15
            )
    finally:
        await task


async def test_restart_tolerates_storage_without_conn(monkeypatch, session_factory):
    class NoConnStorage:
        @staticmethod
        async def api_id():
            return 1

        @staticmethod
        async def open():
            raise AssertionError("open must not be called for a storage without conn")

    monkeypatch.setattr(DummyClient, "connection_factory", _AlwaysFails)
    monkeypatch.setattr(DummyClient, "storage", NoConnStorage)
    monkeypatch.setattr(Session, "MAX_RETRIES", 1)

    with pytest.raises(OSError):
        await asyncio.wait_for(session_factory().restart(), timeout=5)


UPLOAD_PART_SIZES = [0, 1, 3, 4, 252, 253, 254, 255, 256, 1024, 512 * 1024, 512 * 1024 + 3]


def _upload_parts(payload):
    return [
        raw.functions.upload.SaveBigFilePart(
            file_id=7, file_part=1, file_total_parts=64, bytes=payload
        ),
        raw.functions.upload.SaveFilePart(file_id=7, file_part=1, bytes=payload),
    ]


@pytest.mark.parametrize("size", UPLOAD_PART_SIZES)
def test_hand_packed_upload_part_matches_the_generated_writer(size):
    payload = bytes(range(256)) * (size // 256) + bytes(range(size % 256))

    for part in _upload_parts(payload):
        assert _serialize_file_part(part) == part.write(), (
            f"{type(part).__name__} of {size} B serialises differently by hand"
        )


def test_only_upload_parts_take_the_hand_packed_path():
    assert _serialize_file_part(raw.functions.Ping(ping_id=0)) is None


async def test_send_hand_packs_upload_parts_and_declares_their_real_length(
    monkeypatch, session_factory
):
    s = session_factory()
    part = _upload_parts(bytes([0x11]) * (512 * 1024))[0]

    s.connection = type(
        "C",
        (),
        {
            "protocol": type("P", (), {"crypto_executor": None})(),
            "send": staticmethod(lambda payload: _packed()),
        },
    )()

    packed = []
    monkeypatch.setattr(
        "pyrogram.session.session.warpcrypto.pack_message",
        lambda msg_id, seq_no, serialized, *rest: packed.append(bytes(serialized)) or b"p",
    )

    declared = []
    real_factory = s.msg_factory
    s.msg_factory = lambda data, length: declared.append(length) or real_factory(data, length)

    await s.send(part, wait_response=False)

    assert packed[0] == part.write(), "the wire bytes must match the generated writer"
    assert declared == [len(packed[0])], (
        f"declared {declared} but put {len(packed[0])} B on the wire"
    )


class FakeQuery:
    QUALNAME = "functions.test.Fake"


class FakeSession:
    MAX_RETRIES = Session.MAX_RETRIES
    _windowed = False
    WAIT_TIMEOUT = Session.WAIT_TIMEOUT

    def __init__(self, fail_times=0):
        self.sent = 0
        self.fail_times = fail_times
        self.is_started = asyncio.Event()
        self.is_started.set()
        self.last_packet_received = 0
        self.client = type("C", (), {"name": "fake"})()

    async def send(self, query, timeout):
        self.sent += 1
        if self.sent <= self.fail_times:
            raise OSError("boom")
        return "answer"

    async def restart(self):
        pass


async def test_a_caller_that_asks_for_no_retries_still_gets_one_attempt():
    session = FakeSession()

    result = await Session._invoke(session, FakeQuery(), 0, 1, 1)

    assert session.sent == 1
    assert result == "answer"


async def test_a_single_attempt_surfaces_the_real_error():
    session = FakeSession(fail_times=1)

    with pytest.raises(OSError):
        await Session._invoke(session, FakeQuery(), 0, 1, 1)

    assert session.sent == 1


async def test_retries_still_retry():
    session = FakeSession(fail_times=2)

    result = await Session._invoke(session, FakeQuery(), 3, 1, 1)

    assert session.sent == 3
    assert result == "answer"
METHODS = Path(__file__).resolve().parents[1] / "pyrogram" / "methods"


def _handler_names(handler):
    node = handler.type

    if node is None:
        return []

    parts = node.elts if isinstance(node, ast.Tuple) else [node]

    return [p.id if isinstance(p, ast.Name) else getattr(p, "attr", "") for p in parts]


def _retry_loops():
    for path in sorted(METHODS.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))

        for node in ast.walk(tree):
            if not isinstance(node, ast.While):
                continue

            if not (isinstance(node.test, ast.Constant) and node.test.value is True):
                continue

            for child in ast.walk(node):
                if not isinstance(child, ast.Try) or not child.orelse:
                    continue

                if any("FilePartMissing" in _handler_names(h) for h in child.handlers):
                    yield path, child


def _cases():
    return [pytest.param(p, t, id=f"{p.parent.name}/{p.stem}:{t.lineno}") for p, t in _retry_loops()]


def test_the_retry_loops_are_still_there():
    assert len(_cases()) >= 10, (
        "this file guards the upload-retry loops; if they are gone the guard is "
        "checking nothing"
    )


@pytest.mark.parametrize("path,try_node", [(p.values[0], p.values[1]) for p in _cases()],
                         ids=[p.id for p in _cases()])
def test_a_successful_send_is_never_retried(path, try_node):
    # `while True` is there to re-send after FilePartMissing and nothing else. If
    # the success branch can fall off the end - the server answered with an
    # Updates carrying none of the update types the method looks for, which is
    # what a business connection or a suggested post does - the loop sends the
    # very same media again, and again, for as long as that keeps happening.
    last = try_node.orelse[-1]

    assert isinstance(last, (ast.Return, ast.Raise, ast.Break)), (
        f"{path.name}: the success branch of the retry loop ends in "
        f"{type(last).__name__}, so an answer it does not recognise re-sends the "
        "message forever"
    )


class DummyStorage:
    conn = object()

    @staticmethod
    async def api_id():
        return 1

    @staticmethod
    async def open():
        pass


class MsgIdTimeOffsetDummyClient:
    name = "skew"
    app_version = "1.0"
    device_model = "T"
    system_version = "L"
    lang_code = "en"
    proxy = None
    ipv6 = False
    session = None
    disconnect_handler = None
    storage = DummyStorage()


class FakeConn:
    def __init__(self):
        self.protocol = type("P", (), {"crypto_executor": None})()
        self.closed = False

    async def close(self):
        self.closed = True


@pytest.fixture
def clock(monkeypatch):
    state = {"skew": 0.0, "real": time.time(), "mono": 10_000.0}

    class FakeTime:
        @staticmethod
        def time():
            return state["real"] + state["skew"]

        @staticmethod
        def monotonic():
            return state["mono"]

    monkeypatch.setattr(msg_id_mod, "time", FakeTime)
    monkeypatch.setattr(msg_id_mod._MsgIdGenerator, "time_offset", 0.0)
    monkeypatch.setattr(msg_id_mod._MsgIdGenerator, "_last_msg_id", 0)
    monkeypatch.setattr(msg_id_mod._MsgIdGenerator, "_base_wall", state["real"])
    monkeypatch.setattr(msg_id_mod._MsgIdGenerator, "_base_mono", state["mono"])

    return state


@pytest.fixture(autouse=True)
def restore_decrypt():
    original = session_mod.warpcrypto.unpack_message
    yield
    session_mod.warpcrypto.unpack_message = original


def server_msg_id(unixtime):
    return (int(unixtime) << 32) | 1


async def feed(session, body, msg_id):
    blob = body.write()
    payload = (msg_id, 1, len(blob), blob, 32 + len(blob))

    session_mod.warpcrypto.unpack_message = lambda *a, **kw: payload
    await session.handle_packet(b"packet")


def make_session():
    s = Session(MsgIdTimeOffsetDummyClient(), 2, b"\x00" * 256, False, crypto_executor=None)
    s.connection = FakeConn()
    return s


async def test_clock_behind_does_not_kill_own_connection(clock):
    clock["skew"] = -60.0
    s = make_session()

    await feed(s, raw.types.Pong(msg_id=1, ping_id=0), server_msg_id(clock["real"]))
    assert abs(MsgId.time_offset - 60.0) < 2, (
        f"first server packet must set the time offset, got {MsgId.time_offset}"
    )

    await feed(s, raw.types.Pong(msg_id=2, ping_id=0), server_msg_id(clock["real"] + 1))
    assert not s.connection.closed, "a merely skewed clock must not close the connection"
    assert len(s.stored_msg_ids) == 2, "both packets must be accepted"


async def test_outgoing_msg_id_follows_server_clock(clock):
    clock["skew"] = -60.0
    s = make_session()

    await feed(s, raw.types.Pong(msg_id=1, ping_id=0), server_msg_id(clock["real"]))

    sent = s.msg_factory(raw.functions.Ping(ping_id=0)).msg_id
    assert abs((sent >> 32) - int(clock["real"])) <= 1, (
        "outgoing msg_id must track server time, not the wrong local clock"
    )


async def test_bad_msg_notification_frees_the_msg_id_floor(clock):
    clock["skew"] = 400.0
    s = make_session()
    s.stored_msg_ids.append(server_msg_id(clock["real"] - 1))

    too_high = s.msg_factory(raw.functions.Ping(ping_id=0)).msg_id

    await feed(
        s,
        raw.types.BadMsgNotification(bad_msg_id=too_high, bad_msg_seqno=0, error_code=17),
        server_msg_id(clock["real"]),
    )

    assert not s.connection.closed, "the message carrying the fix must not be discarded"
    assert abs(MsgId.time_offset + 400.0) < 2, (
        f"error_code 17 must resync the clock, got {MsgId.time_offset}"
    )

    resent = s.msg_factory(raw.functions.Ping(ping_id=0)).msg_id
    assert resent < too_high, (
        "the resend must drop back below the msg_ids the server rejected"
    )
    assert abs((resent >> 32) - int(clock["real"])) <= 1


async def test_stop_clears_stored_msg_ids_after_draining_packets(clock):
    s = make_session()
    s.stored_msg_ids.append(server_msg_id(clock["real"]))

    async def slow_teardown():
        await asyncio.sleep(0.05)

    async def late_packet():
        await asyncio.sleep(0.01)
        s.stored_msg_ids.append(server_msg_id(clock["real"]) + 2)

    s.ping_task = asyncio.ensure_future(slow_teardown())
    s._packet_tasks.add(asyncio.ensure_future(late_packet()))

    await s.stop()

    assert not s.stored_msg_ids, (
        "a leftover packet must not leave state that skips the next connection's time sync"
    )


async def test_a_lone_stale_packet_is_dropped_without_resyncing(clock):
    s = make_session()
    s.stored_msg_ids.append(server_msg_id(clock["real"] - 7200))
    stale = server_msg_id(clock["real"] - 3600)

    await feed(s, raw.types.Pong(msg_id=1, ping_id=0), stale)

    assert not s.connection.closed, "one stale packet must not cost a reconnect"
    assert stale not in s.stored_msg_ids, "replay protection must still drop it"
    assert MsgId.time_offset == 0.0, (
        "a single out-of-window message must never be allowed to move the clock, "
        "or a replay could drag the whole session out of step"
    )


async def test_a_wall_clock_step_does_not_move_mtproto_time(clock):
    before = MsgId.now()

    clock["skew"] = 900.0

    assert abs(MsgId.now() - before) < 1, (
        "MTProto time must ride the monotonic clock, so an NTP step cannot "
        "invalidate a time offset that was correct a moment earlier"
    )

    clock["mono"] += 5

    assert abs(MsgId.now() - before - 5) < 1, "it must still advance in real time"


async def test_a_clock_step_mid_connection_does_not_reconnect(clock):
    s = make_session()

    await feed(s, raw.types.Pong(msg_id=1, ping_id=0), server_msg_id(clock["real"]))
    await feed(s, raw.types.Pong(msg_id=2, ping_id=0), server_msg_id(clock["real"] + 1))

    clock["skew"] = -600.0

    accepted = server_msg_id(clock["real"] + 2)
    await feed(s, raw.types.Pong(msg_id=3, ping_id=0), accepted)

    assert not s.connection.closed, (
        "the host clock stepping under a live session must not tear it down"
    )
    assert accepted in s.stored_msg_ids, "traffic must keep flowing across the step"


async def test_a_stalled_monotonic_clock_resyncs_after_repeated_breaches(clock):
    s = make_session()

    await feed(s, raw.types.Pong(msg_id=1, ping_id=0), server_msg_id(clock["real"]))

    resumed = clock["real"] + 3600

    for i in range(Session.MAX_SKEW_BREACHES):
        await feed(s, raw.types.Pong(msg_id=2 + i, ping_id=0), server_msg_id(resumed + i))

    assert not s.connection.closed, (
        "a suspended host leaves CLOCK_MONOTONIC behind; that must resync, not reconnect"
    )
    assert abs(MsgId.time_offset - 3600) < 5, (
        f"consecutive breaches must resync the offset, got {MsgId.time_offset}"
    )

    recovered = server_msg_id(resumed + 10)
    await feed(s, raw.types.Pong(msg_id=9, ping_id=0), recovered)

    assert recovered in s.stored_msg_ids, (
        "traffic must be accepted again once the offset has been resynced"
    )


def test_msg_id_shape(clock):
    ids = [MsgId() for _ in range(50)]

    assert all(i % 4 == 0 for i in ids), "client msg_ids must be divisible by 4"
    assert all(i & 0xFFFFFFFF for i in ids), "the low 32 bits must not be empty"
    assert all(b > a for a, b in zip(ids, ids[1:])), "msg_ids must increase monotonically"


@pytest.fixture
def client():
    return pyrogram.Client("auto_no_updates", api_id=1, api_hash="a", in_memory=True)


@pytest.mark.parametrize("query", [
    raw.functions.updates.GetState(),
    raw.functions.updates.GetDifference(pts=1, date=1, qts=1),
    raw.functions.updates.GetChannelDifference(
        channel=raw.types.InputChannelEmpty(),
        filter=raw.types.ChannelMessagesFilterEmpty(),
        pts=1,
        limit=1,
    ),
])
def test_updates_queries_are_never_sent_without_updates(client, query):
    assert client._auto_needs_updates(query) is True


@pytest.mark.parametrize("query", [
    raw.functions.messages.GetHistory(
        peer=raw.types.InputPeerEmpty(), offset_id=0, offset_date=0,
        add_offset=0, limit=1, max_id=0, min_id=0, hash=0,
    ),
    raw.functions.upload.GetFile(
        location=raw.types.InputFileLocation(
            volume_id=0, local_id=0, secret=0, file_reference=b"",
        ),
        offset=0,
        limit=1,
    ),
])
def test_read_only_queries_still_skip_updates(client, query):
    assert client._auto_needs_updates(query) is False


def test_sends_still_need_updates(client):
    query = raw.functions.messages.SendMessage(
        peer=raw.types.InputPeerEmpty(), message="x", random_id=1,
    )

    assert client._auto_needs_updates(query) is True
