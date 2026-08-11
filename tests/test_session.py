import asyncio

import pytest

import pyrogram.session.session as session_mod
from pyrogram import raw
from pyrogram.errors import AuthKeyUnregistered
from pyrogram.session.session import Session


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
    dc_id = 2
    disconnect_handler = None


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
    monkeypatch.setattr(session_mod, "Connection", _AuthFailThenUnreg)

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
    monkeypatch.setattr(session_mod, "Connection", _AlwaysFails)

    started = asyncio.get_event_loop().time()
    with pytest.raises(OSError):
        await asyncio.wait_for(session_factory().start(max_attempts=2), timeout=5)

    elapsed = asyncio.get_event_loop().time() - started
    assert _AlwaysFails.attempts == 2, (
        f"expected start to stop after max_attempts, got {_AlwaysFails.attempts} attempts"
    )
    assert elapsed < 4, f"max_attempts should cap retries, took {elapsed:.1f}s"


async def test_invoke_surfaces_real_start_failure(monkeypatch, session_factory):
    s = session_factory()
    s._start_active = False
    s._start_exc = AuthKeyUnregistered(401, "AUTH_KEY_UNREGISTERED")

    with pytest.raises(AuthKeyUnregistered):
        await s.invoke(raw.functions.Ping(ping_id=0))


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


async def test_invoke_raises_bounded_start_error_after_active_finishes(monkeypatch, session_factory):
    s = session_factory()
    s._start_active = True
    s._start_completed.clear()

    async def _fail_start():
        await asyncio.sleep(0.05)
        s._start_exc = OSError("request timed out")
        s._start_active = False
        s._start_completed.set()

    task = asyncio.ensure_future(_fail_start())
    try:
        with pytest.raises(OSError, match="request timed out"):
            await s.invoke(raw.functions.Ping(ping_id=0), retries=2, timeout=1)
    finally:
        await task