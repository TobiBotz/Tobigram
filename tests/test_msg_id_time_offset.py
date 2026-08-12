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
    monkeypatch.setattr(msg_id_mod._MsgIdGenerator, "time_offset", 0.0)
    monkeypatch.setattr(msg_id_mod._MsgIdGenerator, "_last_msg_id", 0)

    state = {"skew": 0.0, "real": time.time()}

    class FakeTime:
        @staticmethod
        def time():
            return state["real"] + state["skew"]

    monkeypatch.setattr(msg_id_mod, "time", FakeTime)
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


async def test_stale_server_packet_is_still_rejected(clock):
    s = make_session()
    s.stored_msg_ids.append(server_msg_id(clock["real"] - 7200))

    await feed(
        s,
        raw.types.Pong(msg_id=1, ping_id=0),
        server_msg_id(clock["real"] - 3600),
    )

    assert s.connection.closed, "replay protection must survive the time-offset fix"


def test_msg_id_shape(clock):
    ids = [MsgId() for _ in range(50)]

    assert all(i % 4 == 0 for i in ids), "client msg_ids must be divisible by 4"
    assert all(i & 0xFFFFFFFF for i in ids), "the low 32 bits must not be empty"
    assert all(b > a for a, b in zip(ids, ids[1:])), "msg_ids must increase monotonically"
