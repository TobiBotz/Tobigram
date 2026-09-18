from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock

import pytest

from pyrogram import Client, raw


@pytest.mark.asyncio
async def test_client_ping_single_attempt():
    client = Client("test_ping_sess", in_memory=True)
    mock_pong = raw.types.Pong(msg_id=123456789, ping_id=987654321)

    async def mock_invoke(query, *args, **kwargs):
        assert isinstance(query, raw.functions.Ping)
        assert query.ping_id > 0
        await asyncio.sleep(0.01)  # simulate network round trip
        return mock_pong

    client.invoke = AsyncMock(side_effect=mock_invoke)

    latency = await client.ping()
    assert isinstance(latency, float)
    assert latency > 0.0
    assert client.invoke.call_count == 1


@pytest.mark.asyncio
async def test_client_ping_multiple_attempts():
    client = Client("test_ping_sess", in_memory=True)
    mock_pong = raw.types.Pong(msg_id=123456789, ping_id=987654321)

    async def mock_invoke(query, *args, **kwargs):
        assert isinstance(query, raw.functions.Ping)
        assert query.ping_id > 0
        await asyncio.sleep(0.005)
        return mock_pong

    client.invoke = AsyncMock(side_effect=mock_invoke)

    latency = await client.ping(attempts=3)
    assert isinstance(latency, float)
    assert latency > 0.0
    assert client.invoke.call_count == 3


@pytest.mark.asyncio
async def test_client_ping_invalid_attempts_fallback():
    client = Client("test_ping_sess", in_memory=True)
    mock_pong = raw.types.Pong(msg_id=123456789, ping_id=987654321)

    client.invoke = AsyncMock(return_value=mock_pong)

    # Negative or zero attempts should fallback to at least 1
    latency = await client.ping(attempts=0)
    assert isinstance(latency, float)
    assert client.invoke.call_count == 1
