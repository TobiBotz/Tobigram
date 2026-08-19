import asyncio
import time

import pytest

from pyrogram import raw
from pyrogram.session.internals import msg_id as msg_id_mod
from pyrogram.session.internals import MsgId
from pyrogram.session.session import Session


class DummyStorage:
    conn = object()

    @staticmethod
    async def api_id():
        return 1

    @staticmethod
    async def open():
        pass


class DummyClient:
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


def server_msg_id(unixtime):
    return (int(unixtime) << 32) | 1


async def feed(session, body, msg_id):
    blob = body.write()
    payload = (msg_id, 1, len(blob), blob, 32 + len(blob))

    async def ret():
        return payload

    session.loop.run_in_executor = lambda ex, fn, *a: ret()
    await session.handle_packet(b"packet")


def make_session():
    s = Session(DummyClient(), 2, b"\x00" * 256, False, crypto_executor=None)
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
