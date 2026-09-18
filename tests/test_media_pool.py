from __future__ import annotations

import asyncio
import inspect

import pytest

from pyrogram import Client


class FakeSession:
    auth_key = b"k"
    server_address = "127.0.0.1"
    port = 443

    def __init__(self):
        self.is_started = asyncio.Event()
        self.is_started.set()
        self.is_restarting = False


def make_client(monkeypatch):
    client = Client.__new__(Client)
    client.media_session_pools = {}
    client._media_pool_demand = {}
    client._media_sessions_locks = {}
    client._session_creation_gate = asyncio.Semaphore(4)

    created = []

    async def fake_get_session(dc_id, is_media=False):
        return FakeSession()

    async def fake_make(dc_id, auth_key, server_address, port):
        created.append(dc_id)
        return FakeSession()

    client.get_session = fake_get_session
    client._make_media_session = fake_make
    return client, created


@pytest.mark.asyncio
async def test_single_transfer_pool_is_unchanged(monkeypatch):
    client, created = make_client(monkeypatch)

    async with client._media_pool(2, 5) as task:
        pool = await task

    assert len(pool) == 5
    assert len(created) == 5
    assert client._media_pool_demand == {}


@pytest.mark.asyncio
async def test_concurrent_transfers_add_capacity(monkeypatch):
    client, _ = make_client(monkeypatch)

    async with client._media_pool(2, 5) as first:
        pool_a = await first

        async with client._media_pool(2, 5) as second:
            pool_b = await second

            assert len(pool_a) == 5
            assert len(pool_b) == 10, "second transfer must add sessions, not share"


@pytest.mark.asyncio
async def test_pool_is_capped(monkeypatch):
    client, _ = make_client(monkeypatch)

    async with client._media_pool(2, 12) as a:
        await a
        async with client._media_pool(2, 12) as b:
            pool = await b

    assert len(pool) == Client.MEDIA_POOL_CAP


@pytest.mark.asyncio
async def test_demand_released_on_error(monkeypatch):
    client, _ = make_client(monkeypatch)

    with pytest.raises(RuntimeError):
        async with client._media_pool(2, 5) as task:
            await task
            raise RuntimeError("transfer blew up")

    assert client._media_pool_demand == {}

    async with client._media_pool(2, 5) as task:
        pool = await task

    assert len(pool) == 5


@pytest.mark.asyncio
async def test_parallel_leases_are_serialised(monkeypatch):
    client, created = make_client(monkeypatch)

    async def transfer():
        async with client._media_pool(2, 5) as task:
            pool = await task
            await asyncio.sleep(0)
            return len(pool)

    sizes = await asyncio.gather(*(transfer() for _ in range(4)))

    assert max(sizes) == Client.MEDIA_POOL_CAP
    assert len(created) == Client.MEDIA_POOL_CAP
    assert client._media_pool_demand == {}


@pytest.mark.asyncio
async def test_a_finished_burst_does_not_inflate_the_next_transfer(monkeypatch):
    from pyrogram.client import Client as RealClient

    source = inspect.getsource(RealClient.get_file)

    assert "dl_pool_size * dl_workers_per_session" in source
    assert "n_sessions) * dl_workers_per_session" not in source
    assert "max(n_sessions, 1) * dl_workers_per_session" not in source


@pytest.mark.asyncio
async def test_pool_survives_a_lease_but_the_demand_does_not(monkeypatch):
    client, created = make_client(monkeypatch)

    async with client._media_pool(2, 5) as a:
        await a
        async with client._media_pool(2, 5) as b:
            await b

    assert len(client.media_session_pools[2]) == 10
    assert client._media_pool_demand == {}

    async with client._media_pool(2, 5) as task:
        pool = await task

    assert len(pool) == 10, "an existing pool is reused, not rebuilt"
    assert len(created) == 10, "and no extra sessions are opened for it"
