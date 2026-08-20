import asyncio
import time
from datetime import datetime, timedelta

import pytest

import pyrogram
from pyrogram import raw
from pyrogram.errors import UnknownError
from pyrogram.errors.rpc_error import RPCError
from pyrogram.storage import SQLiteStorage

from tests.test_audit_regressions import make_dispatcher


class _WatchdogClient:
    UPDATES_WATCHDOG_INTERVAL = 0.05
    updates_watchdog = pyrogram.Client.updates_watchdog

    def __init__(self):
        self.updates_watchdog_event = asyncio.Event()
        self.calls = 0

        # an update arrived an hour of monotonic time ago, and the host clock
        # then stepped back an hour, so the wall-clock stamp is in the future
        self.last_update_time = datetime.now() + timedelta(hours=1)
        self._last_update_monotonic = time.monotonic() - 3600

    async def invoke(self, query, **kwargs):
        self.calls += 1

    async def recover_gaps(self):
        return (0, 0)


async def test_the_updates_watchdog_measures_idle_time_on_the_monotonic_clock():
    client = _WatchdogClient()

    task = asyncio.ensure_future(client.updates_watchdog())
    await asyncio.sleep(0.3)

    try:
        assert client.calls > 0, (
            "idle time is a duration, so a host clock that steps backwards must "
            "not stall the watchdog for the length of the step"
        )
    finally:
        client.updates_watchdog_event.set()
        await asyncio.wait_for(task, timeout=5)


async def test_a_small_write_batch_is_committed_without_waiting_for_more(monkeypatch, tmp_path):
    monkeypatch.setattr(SQLiteStorage, "_AUTO_COMMIT_SECONDS", 0.1)

    storage = SQLiteStorage("bounded", tmp_path, in_memory=True)
    await storage.open()

    try:
        await storage.update_peers([(1, 2, "user", None)])

        assert storage._dirty, "one write is below the batch size, so it is still pending"

        await asyncio.sleep(0.4)

        assert not storage._dirty, (
            "a batch that never reaches its size sits in an open write transaction "
            "for as long as the process runs; a kill loses it and the transaction "
            "keeps the WAL from being checkpointed"
        )
    finally:
        await storage.close()


async def test_a_stopped_dispatcher_leaves_nothing_in_its_queue():
    dispatcher = make_dispatcher()

    await dispatcher.start()

    # a worker cancelled during a previous stop never took its sentinel
    dispatcher.updates_queue.put_nowait(None)

    await dispatcher.stop()

    assert dispatcher.updates_queue.empty(), (
        "a sentinel left in the queue retires a worker of the next generation the "
        "instant it starts, and parsed updates left there hold their peer graphs"
    )

    await dispatcher.start()
    await asyncio.sleep(0.05)
    dispatcher.prune_workers()

    assert len(dispatcher.handler_worker_tasks) == dispatcher.client.workers, (
        "every worker of a freshly started dispatcher must still be running"
    )

    await dispatcher.stop()


def _unknown():
    RPCError.raise_it(
        raw.types.RpcError(error_code=999, error_message="NOT_A_REAL_ERROR"),
        raw.functions.Ping,
    )


async def test_an_unknown_error_does_not_write_to_the_working_directory(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    with pytest.raises(UnknownError):
        _unknown()

    assert not (tmp_path / "unknown_errors.txt").exists(), (
        "a library must not append to a file in the caller's working directory, "
        "unbounded, from inside an exception constructor"
    )


async def test_an_unwritable_working_directory_does_not_replace_the_error(monkeypatch):
    import builtins

    real_open = builtins.open

    def refusing_open(*args, **kwargs):
        if args and str(args[0]).endswith("unknown_errors.txt"):
            raise OSError(30, "Read-only file system")
        return real_open(*args, **kwargs)

    monkeypatch.setattr(builtins, "open", refusing_open)

    with pytest.raises(UnknownError):
        _unknown()
