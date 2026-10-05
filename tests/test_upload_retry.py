import asyncio
from types import SimpleNamespace

import pytest

import pyrogram.methods.advanced.save_file as save_file_mod
import pyrogram.session.session as session_mod
from pyrogram.errors import FilePartTooBig, FloodWait, ServiceUnavailable
from tests.e2e import CHUNK, FakeDC, make_client


class Asyncio:
    def __init__(self, slept):
        self.slept = slept

    def __getattr__(self, name):
        return getattr(asyncio, name)

    async def sleep(self, delay, *args):
        if delay:
            self.slept.append(delay)
        await asyncio.sleep(0)


async def upload(tmp_path, monkeypatch, fail, size=4 * CHUNK):
    path = tmp_path / "up.bin"
    path.write_bytes(b"\x01" * size)

    slept = []
    monkeypatch.setattr(save_file_mod, "asyncio", Asyncio(slept))
    monkeypatch.setattr(session_mod, "asyncio", Asyncio([]))

    dc = FakeDC(size, step=0)
    client = make_client(dc, "upretry", sessions=2)
    client.me = SimpleNamespace(is_bot=False, is_premium=False)
    await client.storage.open()

    attempts = []

    for session in await client._get_media_session_pool(2, 2):
        real = session.send

        async def send(query, wait_response=True, timeout=None, retry=0, real=real):
            attempts.append(query)
            error = fail(len(attempts))
            if error is not None:
                raise error
            return await real(query, wait_response, timeout, retry)

        session.send = send

    result = await asyncio.wait_for(client.save_file(str(path)), timeout=30)
    return result, attempts, slept


async def test_a_part_the_server_refuses_fails_the_upload_at_once(tmp_path, monkeypatch):
    attempts = []

    def fail(n):
        attempts.append(n)
        return FilePartTooBig(rpc_name="upload.SaveFilePart")

    with pytest.raises(FilePartTooBig):
        await upload(tmp_path, monkeypatch, fail)

    assert len(attempts) <= 8, (
        f"{len(attempts)} sends of parts the server refuses outright; only a "
        "flood wait, a 5xx or a lost connection can succeed on a retry"
    )


async def test_a_flood_wait_sleeps_what_the_server_asked(tmp_path, monkeypatch):
    result, _, slept = await upload(
        tmp_path,
        monkeypatch,
        lambda n: FloodWait(value=42, rpc_name="upload.SaveFilePart") if n == 1 else None,
    )

    assert result is not None
    assert 42 in slept, f"slept {slept}; the server asked for 42 seconds"


async def test_a_503_storm_is_still_ridden_out(tmp_path, monkeypatch):
    result, attempts, _ = await upload(
        tmp_path,
        monkeypatch,
        lambda n: ServiceUnavailable(rpc_name="upload.SaveFilePart") if n <= 12 else None,
    )

    assert result is not None
    assert len(attempts) > 12
