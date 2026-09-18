import asyncio
from hashlib import sha256

import pytest

from pyrogram import raw
from pyrogram.crypto import aes
from pyrogram.errors import CDNFileHashMismatch

from .e2e import CHUNK, FakeDC, document, make_client

SIZE = 8 * CHUNK
HASH_LIMIT = 128 * 1024
KEY = bytes(range(32))
IV = bytes(range(16))


def plain(offset, length):
    return bytes([(offset // CHUNK) & 0xFF]) * length


def iv_for(offset):
    return bytearray(IV[:-4] + (offset // 16).to_bytes(4, "big"))


def window(offset, length):
    out = bytearray()
    at = offset

    while at < offset + length:
        chunk_end = (at // CHUNK + 1) * CHUNK
        take = min(chunk_end, offset + length) - at
        out += plain(at, take)
        at += take

    return bytes(out)


class CdnDC(FakeDC):
    def __init__(self, size, hash_span, seed_hashes=False, corrupt_at=None):
        super().__init__(size)

        self.hash_span = hash_span
        self.seed_hashes = seed_hashes
        self.corrupt_at = corrupt_at
        self.hash_requests = 0

    def hashes_from(self, start):
        out = []
        at = start

        while at < min(start + self.hash_span, self.file_size):
            length = min(HASH_LIMIT, self.file_size - at)
            out.append(
                raw.types.FileHash(
                    offset=at, limit=HASH_LIMIT, hash=sha256(window(at, length)).digest()
                )
            )
            at += HASH_LIMIT

        return out

    def _send_for(self, session):
        async def send(query, wait_response=True, timeout=None, retry=0):
            await asyncio.sleep(0)
            return self._answer(query)

        return send

    def _answer(self, query):
        inner = getattr(query, "query", query)

        if isinstance(inner, raw.functions.upload.GetFile):
            return raw.types.upload.FileCdnRedirect(
                dc_id=203,
                file_token=b"token",
                encryption_key=KEY,
                encryption_iv=IV,
                file_hashes=self.hashes_from(0) if self.seed_hashes else [],
            )

        if isinstance(inner, raw.functions.upload.GetCdnFile):
            length = min(CHUNK, max(0, self.file_size - inner.offset))
            data = bytearray(plain(inner.offset, length))

            if length and inner.offset == self.corrupt_at:
                data[0] ^= 0xFF

            return raw.types.upload.CdnFile(
                bytes=aes.ctr256_encrypt(bytes(data), KEY, iv_for(inner.offset))
            )

        if isinstance(inner, raw.functions.upload.GetCdnFileHashes):
            self.hash_requests += 1
            return self.hashes_from(inner.offset)

        return super()._answer(inner)


async def download(dc):
    client = make_client(dc, sessions=4)

    async def stop():
        pass

    for session in await client._get_media_session_pool(2, 4):
        session.stop = stop

    total = 0

    async for chunk in client.get_file(document(), SIZE):
        total += len(chunk)

    return total


@pytest.mark.parametrize("hash_span", [CHUNK, 2 * CHUNK, SIZE])
async def test_cdn_download_accepts_hashes_reaching_past_the_chunk(hash_span):
    assert await download(CdnDC(SIZE, hash_span)) == SIZE


async def test_cdn_download_reuses_hashes_it_already_holds():
    per_chunk = CdnDC(SIZE, CHUNK)
    ahead = CdnDC(SIZE, SIZE)
    seeded = CdnDC(SIZE, SIZE, seed_hashes=True)

    assert await download(per_chunk) == SIZE
    assert await download(ahead) == SIZE
    assert await download(seeded) == SIZE

    assert per_chunk.hash_requests == SIZE // CHUNK
    assert ahead.hash_requests == 1
    assert seeded.hash_requests == 0


async def test_cdn_download_still_rejects_a_corrupted_chunk():
    with pytest.raises(CDNFileHashMismatch):
        await download(CdnDC(SIZE, SIZE, seed_hashes=True, corrupt_at=4 * CHUNK))


async def test_cdn_download_writes_every_chunk_to_disk(tmp_path):
    dc = CdnDC(SIZE, SIZE, seed_hashes=True)
    client = make_client(dc, sessions=4)

    async def stop():
        pass

    for session in await client._get_media_session_pool(2, 4):
        session.stop = stop

    path = await client.handle_download(
        (document(), str(tmp_path), "cdn.bin", False, SIZE, None, ())
    )

    with open(path, "rb") as handle:
        data = handle.read()

    assert len(data) == SIZE

    for n in range(SIZE // CHUNK):
        assert data[n * CHUNK : (n + 1) * CHUNK] == bytes([n]) * CHUNK
