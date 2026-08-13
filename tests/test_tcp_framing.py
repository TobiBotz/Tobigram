import asyncio

import pytest

from pyrogram.connection.transport.tcp.tcp import TCP
from pyrogram.connection.transport.tcp.tcp_abridged import TCPAbridged
from pyrogram.session.session import Session


def frame(payload: bytes) -> bytes:
    return bytes([len(payload) // 4]) + payload


class ScriptedReader:
    def __init__(self, *parts):
        self.parts = list(parts)
        self.buf = b""

    async def read(self, n):
        while not self.buf:
            if not self.parts:
                return b""
            part = self.parts.pop(0)
            if part == "STALL":
                await asyncio.sleep(3600)
            self.buf = part
        out, self.buf = self.buf[:n], self.buf[n:]
        return out


@pytest.fixture
def quick_timeout(monkeypatch):
    monkeypatch.setattr(TCP, "TIMEOUT", 0.05)


def make_protocol(reader):
    protocol = TCPAbridged(False, None)
    protocol.reader = reader
    return protocol


async def test_a_stall_before_any_byte_stays_recoverable(quick_timeout):
    protocol = make_protocol(ScriptedReader("STALL", frame(b"A" * 8)))

    with pytest.raises(TimeoutError):
        await protocol.recv()


async def test_a_stall_mid_message_is_reported_as_a_broken_connection(quick_timeout):
    body = b"A" * 64
    head = frame(body)
    protocol = make_protocol(ScriptedReader(head[:33], "STALL", head[33:]))

    with pytest.raises(OSError) as exc:
        await protocol.recv()

    assert not isinstance(exc.value, TimeoutError)


async def test_a_stall_after_the_extended_length_marker_is_broken_too(quick_timeout):
    protocol = make_protocol(ScriptedReader(b"\x7f", "STALL", b"\x01\x00\x00"))

    with pytest.raises(OSError) as exc:
        await protocol.recv()

    assert not isinstance(exc.value, TimeoutError)


class FakeConn:
    def __init__(self, *packets):
        self.packets = list(packets)
        self.protocol = type("P", (), {"crypto_executor": None})()

    async def recv(self):
        if not self.packets:
            return None
        return self.packets.pop(0)

    async def close(self):
        pass


class DummyClient:
    name = "framing"
    app_version = "1.0"
    device_model = "T"
    system_version = "L"
    lang_code = "en"
    proxy = None
    ipv6 = False
    session = None
    disconnect_handler = None


def make_session(conn):
    session = Session(DummyClient(), 2, b"k" * 256, False)
    session.connection = conn
    session.loop = asyncio.get_running_loop()
    return session


async def test_an_empty_packet_ends_the_read_loop():
    session = make_session(FakeConn(b""))
    handled = []
    session._handle_packet_wrapper = lambda p: handled.append(p)

    await asyncio.wait_for(session.recv_worker(), 5)

    assert handled == []


async def test_an_undecryptable_packet_does_not_look_like_a_live_connection():
    session = make_session(FakeConn(b"garbage-that-cannot-decrypt", None))

    await asyncio.wait_for(session.recv_worker(), 5)
    await asyncio.sleep(0)

    assert session.last_packet_received == 0.0
