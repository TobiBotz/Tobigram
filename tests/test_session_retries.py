import asyncio

import pytest

from pyrogram.session.session import Session


class FakeQuery:
    QUALNAME = "functions.test.Fake"


class FakeSession:
    MAX_RETRIES = Session.MAX_RETRIES
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
