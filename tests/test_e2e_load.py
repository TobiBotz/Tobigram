import asyncio
import os

import pyrogram
from pyrogram.client import write_at
from pyrogram.session.session import Session

from .e2e import (
    CHUNK,
    FakeDC,
    TrackingDC,
    document,
    download_to,
    expected_byte,
    make_client,
    measure,
    stream_all,
)

FILE = 20 * CHUNK
FAST = 0.0005


def clients(dc, count, **kwargs):
    return [make_client(dc, f"e2e{i}", **kwargs) for i in range(count)]


async def run_streams(dc, count, client_count=1, verify=False):
    cs = clients(dc, client_count)

    async def go():
        await asyncio.gather(*(
            stream_all(cs[i % client_count], dc.file_size, verify=verify)
            for i in range(count)
        ))

    return await measure(go, dc), cs


async def run_downloads(dc, count, tmp_path, client_count=1):
    cs = clients(dc, client_count)

    async def go():
        await asyncio.gather(*(
            download_to(cs[i % client_count], dc.file_size, tmp_path / f"f{i}.bin")
            for i in range(count)
        ))

    return await measure(go, dc), cs


def test_parts_are_written_at_an_offset_on_every_platform(tmp_path):
    path = tmp_path / "offsets.bin"

    with open(path, "w+b") as handle:
        handle.truncate(4096)
        fd = handle.fileno()
        write_at(fd, b"C" * 1024, 2048)
        write_at(fd, b"A" * 1024, 0)
        write_at(fd, b"B" * 1024, 1024)

    data = path.read_bytes()

    assert data[0:1024] == b"A" * 1024
    assert data[1024:2048] == b"B" * 1024
    assert data[2048:3072] == b"C" * 1024


def test_writing_at_an_offset_leaves_the_rest_of_the_file_alone(tmp_path):
    path = tmp_path / "sparse.bin"

    with open(path, "w+b") as handle:
        handle.write(b"\xff" * 3072)
        handle.flush()
        write_at(handle.fileno(), b"\x00" * 1024, 1024)

    data = path.read_bytes()

    assert data[0:1024] == b"\xff" * 1024
    assert data[1024:2048] == b"\x00" * 1024
    assert data[2048:3072] == b"\xff" * 1024


async def test_a_download_terminates_when_the_workers_run_out_of_work():
    dc = FakeDC(FILE, step=FAST)
    client = make_client(dc)

    got = await asyncio.wait_for(stream_all(client, FILE), timeout=30)

    assert got == FILE


async def test_many_downloads_all_terminate():
    dc = FakeDC(FILE, step=FAST)

    result, _ = await asyncio.wait_for(run_streams(dc, 30), timeout=120)

    assert result.dc.served == 30 * (FILE // CHUNK)


async def test_chunks_arrive_in_order_under_load():
    dc = FakeDC(FILE, step=FAST)

    await asyncio.wait_for(run_streams(dc, 8, verify=True), timeout=60)


async def test_a_download_writes_the_right_bytes_at_high_concurrency(tmp_path):
    dc = FakeDC(FILE, step=FAST)

    _result, _cs = await asyncio.wait_for(run_downloads(dc, 12, tmp_path), timeout=120)

    for i in range(12):
        data = (tmp_path / f"f{i}.bin").read_bytes()
        assert len(data) == FILE

        for part in range(FILE // CHUNK):
            window = data[part * CHUNK: part * CHUNK + 16]
            assert set(window) == {expected_byte(part)}, (
                f"file {i} part {part} landed at the wrong offset"
            )


async def test_nothing_times_out_at_thirty_parallel_downloads():
    dc = FakeDC(FILE, step=FAST)

    result, _ = await asyncio.wait_for(run_streams(dc, 30), timeout=120)

    assert result.dc.timeouts == 0


async def test_one_connection_never_exceeds_the_media_cap():
    dc = TrackingDC(FILE, step=FAST)

    await asyncio.wait_for(run_streams(dc, 30), timeout=120)

    assert dc.worst_connection <= Session.MAX_INFLIGHT_MEDIA


async def test_streaming_thirty_files_stays_within_the_read_ahead_budget():
    dc = FakeDC(FILE, step=FAST)

    result, _ = await asyncio.wait_for(run_streams(dc, 30), timeout=120)

    budget = pyrogram.Client.MAX_READ_AHEAD_CHUNKS + Session.MAX_INFLIGHT_MEDIA * 3

    assert result.peak_mib < budget + 24, (
        f"{result.peak_mib:.0f} MiB peak for 30 parallel streams; the read-ahead "
        f"budget is {budget} chunks, so this is not bounded by it"
    )


async def test_downloading_thirty_files_to_disk_barely_uses_memory(tmp_path):
    dc = FakeDC(FILE, step=FAST)

    result, _ = await asyncio.wait_for(run_downloads(dc, 30, tmp_path), timeout=180)

    assert result.peak_mib < 48, (
        f"{result.peak_mib:.0f} MiB peak writing 30 files straight to disk; parts "
        "should not be held once written"
    )


async def test_download_memory_does_not_grow_with_concurrency(tmp_path):
    (tmp_path / "low").mkdir()
    (tmp_path / "high").mkdir()

    low, _ = await asyncio.wait_for(
        run_downloads(FakeDC(FILE, step=FAST), 8, tmp_path / "low"), timeout=120
    )
    high, _ = await asyncio.wait_for(
        run_downloads(FakeDC(FILE, step=FAST), 24, tmp_path / "high"), timeout=180
    )

    assert high.peak_mib < low.peak_mib * 3, (
        f"tripling the concurrency took memory from {low.peak_mib:.0f} to "
        f"{high.peak_mib:.0f} MiB, so something scales per transfer"
    )


async def test_two_clients_in_parallel_do_not_time_out():
    dc = FakeDC(FILE, step=FAST)

    result, _ = await asyncio.wait_for(run_streams(dc, 20, client_count=2), timeout=120)

    assert result.dc.timeouts == 0


async def test_two_clients_each_bound_their_own_read_ahead():
    dc = FakeDC(FILE, step=FAST)

    one, _ = await asyncio.wait_for(run_streams(dc, 20, client_count=1), timeout=120)
    two, _ = await asyncio.wait_for(
        run_streams(FakeDC(FILE, step=FAST), 20, client_count=2), timeout=120
    )

    assert two.peak_mib < one.peak_mib * 2.5, (
        f"one client peaked at {one.peak_mib:.0f} MiB and two at {two.peak_mib:.0f}; "
        "each client should add its own bounded budget, not multiply the total"
    )


async def test_the_read_ahead_budget_comes_back_after_every_transfer():
    dc = FakeDC(FILE, step=FAST)
    client = make_client(dc)
    before = client.read_ahead_slots._value

    await asyncio.wait_for(
        asyncio.gather(*(stream_all(client, FILE) for _ in range(6))), timeout=60
    )

    assert client.read_ahead_slots._value == before


async def test_the_read_ahead_budget_comes_back_after_an_abandoned_stream():
    dc = FakeDC(FILE, step=FAST)
    client = make_client(dc)
    before = client.read_ahead_slots._value

    for _ in range(8):
        stream = client.get_file(document(), FILE)
        taken = 0
        async for _chunk in stream:
            taken += 1
            if taken == 5:
                break
        await stream.aclose()

    assert client.read_ahead_slots._value == before, (
        "a stream abandoned part way leaks its buffered slots, and the budget is "
        "shared, so the client eventually stops transferring altogether"
    )


async def test_an_abandoned_stream_does_not_wedge_later_transfers():
    dc = FakeDC(FILE, step=FAST)
    client = make_client(dc)

    for _ in range(12):
        stream = client.get_file(document(), FILE)
        taken = 0
        async for _chunk in stream:
            taken += 1
            if taken == 5:
                break
        await stream.aclose()

    assert await asyncio.wait_for(stream_all(client, FILE), timeout=30) == FILE


async def test_transfers_leave_no_tasks_behind():
    dc = FakeDC(FILE, step=FAST)
    client = make_client(dc)
    before = len(asyncio.all_tasks())

    await asyncio.wait_for(
        asyncio.gather(*(stream_all(client, FILE) for _ in range(8))), timeout=60
    )
    await asyncio.sleep(0.1)

    assert len(asyncio.all_tasks()) <= before + 1


async def test_uploads_do_not_buffer_the_whole_file(tmp_path):
    size = 40 * CHUNK
    path = tmp_path / "upload.bin"

    with open(path, "wb") as handle:
        handle.truncate(size)

    dc = FakeDC(size, step=FAST)
    client = make_client(dc, pool=dc.pool(14))
    await client.storage.open()

    result = await measure(lambda: client.save_file(str(path)), dc)

    assert result.peak_mib < size / CHUNK / 2, (
        f"{result.peak_mib:.0f} MiB peak uploading a {size // CHUNK} MiB file; the "
        "pipeline should hold a bounded window, not most of the file"
    )


async def test_upload_memory_does_not_grow_with_the_file(tmp_path):
    def make(name, size):
        path = tmp_path / name
        with open(path, "wb") as handle:
            handle.truncate(size)
        return str(path)

    small = make("small.bin", 20 * CHUNK)
    large = make("large.bin", 80 * CHUNK)

    async def upload(path, size):
        dc = FakeDC(size, step=FAST)
        client = make_client(dc, pool=dc.pool(14))
        await client.storage.open()
        return await measure(lambda: client.save_file(path), dc)

    low = await upload(small, 20 * CHUNK)
    high = await upload(large, 80 * CHUNK)

    assert high.peak_mib < low.peak_mib * 2, (
        f"a 4x larger file took memory from {low.peak_mib:.0f} to "
        f"{high.peak_mib:.0f} MiB, so the upload window tracks the file size"
    )
