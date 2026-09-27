from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from pyrogram.methods.auth.initialize import Initialize
from pyrogram.methods.auth.terminate import Terminate


class MockClient(Initialize, Terminate):
    def __init__(self, no_updates: bool = False):
        self.is_connected = True
        self.is_initialized = False
        self.no_updates = no_updates
        self.rate_limiter = None
        self.takeout_id = None
        self.listeners = MagicMock()
        self.listeners.close = AsyncMock()
        self.storage = MagicMock()
        self.storage.save = AsyncMock()
        self.dispatcher = MagicMock()
        self.dispatcher.start = AsyncMock()
        self.dispatcher.stop = AsyncMock()
        self.media_pool_reaper_event = asyncio.Event()
        self.media_pool_reaper_task = None
        self.updates_watchdog_event = asyncio.Event()
        self.updates_watchdog_task = None
        self.sessions = {}
        self.media_sessions = {}
        self.media_session_pools = {}

    def load_plugins(self):
        pass

    async def updates_watchdog(self):
        await asyncio.Event().wait()

    async def media_pool_reaper(self):
        pass


@pytest.mark.asyncio
async def test_no_updates_client_does_not_start_watchdog():
    client = MockClient(no_updates=True)

    await client.initialize()
    try:
        assert client.updates_watchdog_task is None
    finally:
        await client.terminate()


@pytest.mark.asyncio
async def test_regular_client_starts_watchdog():
    client = MockClient(no_updates=False)

    await client.initialize()
    try:
        assert client.updates_watchdog_task is not None
        assert not client.updates_watchdog_task.done()
    finally:
        await client.terminate()
        assert client.updates_watchdog_task is None


@pytest.mark.asyncio
async def test_terminate_cancels_in_flight_watchdog_immediately():
    client = MockClient(no_updates=False)

    await client.initialize()
    task = client.updates_watchdog_task
    assert task is not None

    # Terminate should cancel the task and finish without hanging
    await asyncio.wait_for(client.terminate(), timeout=1.0)
    assert task.cancelled() or task.done()
    assert client.updates_watchdog_task is None
