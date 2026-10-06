#  Pyrogram - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-present Dan <https://github.com/delivrance>
#
#  This file is part of Pyrogram.
#
#  Pyrogram is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Pyrogram is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with Pyrogram.  If not, see <http://www.gnu.org/licenses/>.

import asyncio
import inspect
import io
import os
import pathlib
import tempfile
from hashlib import sha256
from types import SimpleNamespace

import pytest

import pyrogram
from pyrogram import raw, enums, types, Client, utils
from pyrogram.crypto import aes
from pyrogram.errors import CDNFileHashMismatch
from pyrogram.file_id import FileType, FileId
from tests.e2e import FakeDC, document, make_client as make_e2e_client


CHUNK = 1024 * 1024


class FakeSession:
    def __init__(self, chunks):
        self.chunks = list(chunks)

    async def invoke(self, query, **kwargs):
        offset = query.offset
        index = offset // CHUNK
        data = self.chunks[index] if index < len(self.chunks) else b""
        return raw.types.upload.File(
            type=raw.types.storage.FileUnknown(),
            mtime=0,
            bytes=data,
        )


class FakeClient:
    get_file = pyrogram.Client.get_file
    handle_download = pyrogram.Client.handle_download
    read_ahead_slots = pyrogram.Client.read_ahead_slots
    MAX_READ_AHEAD_CHUNKS = pyrogram.Client.MAX_READ_AHEAD_CHUNKS
    MEDIA_POOL_CAP = pyrogram.Client.MEDIA_POOL_CAP
    _media_pool = pyrogram.Client._media_pool

    def __init__(self, chunks):
        self.get_file_semaphore = asyncio.Semaphore(1)
        self._media_pool_demand = {}
        self.me = SimpleNamespace(is_bot=True, is_premium=False)
        self.session = FakeSession(chunks)

    async def get_session(self, dc_id, is_media=False):
        return self.session

    async def _get_media_session_pool(self, dc_id, size):
        return [self.session]


def file_id():
    return SimpleNamespace(
        file_type=FileType.DOCUMENT,
        media_id=1,
        access_hash=1,
        file_reference=b"",
        thumbnail_size="",
        dc_id=2,
    )


async def download(tmp_path, chunks, file_size):
    client = FakeClient(chunks)
    path = await client.handle_download(
        (file_id(), str(tmp_path), "out.bin", False, file_size, None, ())
    )
    with open(path, "rb") as f:
        return f.read()


@pytest.mark.parametrize(
    "chunks",
    [
        [b"x" * 2048],  # single short chunk
        [b"a" * CHUNK, b"b" * 4096],  # spills into the sequential loop
    ],
)
async def test_unknown_size_download_is_written(tmp_path, chunks):
    # Telegram reports file_size 0 for some media; the bytes must still land on disk.
    assert await download(tmp_path, chunks, 0) == b"".join(chunks)


async def test_known_size_download_is_written(tmp_path):
    data = b"x" * 2048
    assert await download(tmp_path, [data], len(data)) == data


class ShortAfterFirstSession(FakeSession):
    """A datacentre that answers every part after the first with a short one."""

    def __init__(self):
        self.served = 0

    async def invoke(self, query, **kwargs):
        self.served += 1
        return raw.types.upload.File(
            type=raw.types.storage.FileUnknown(),
            mtime=0,
            bytes=b"x" * (CHUNK if query.offset == 0 else CHUNK // 2),
        )


async def test_a_download_ends_when_its_workers_do(tmp_path):
    # every parallel worker retires on its first short part, so offsets are left
    # unclaimed and the completion count never reaches the chunk count
    client = FakeClient([])
    client.session = ShortAfterFirstSession()

    path = await asyncio.wait_for(
        client.handle_download((file_id(), str(tmp_path), "out.bin", False, 20 * CHUNK, None, ())),
        timeout=10,
    )

    assert path is not None


FILE_ID = FileId(file_type=FileType.DOCUMENT, dc_id=2, media_id=1, access_hash=1).encode()
STRIPPED = bytes([0x01, 0x20, 0x20]) + bytes(range(64)) * 3
MEDIA_ATTRIBUTES = (
    "audio",
    "document",
    "photo",
    "sticker",
    "animation",
    "video",
    "voice",
    "video_note",
    "new_chat_photo",
    "paid_media",
    "story",
    "reply_to_story",
    "media",
)


def blank(cls):
    obj = object.__new__(cls)

    for name in MEDIA_ATTRIBUTES:
        try:
            setattr(obj, name, None)
        except Exception:
            pass

    return obj


def fake_media(file_name):
    return SimpleNamespace(
        file_id=FILE_ID,
        file_name=file_name,
        file_size=10,
        mime_type="application/octet-stream",
        date=None,
    )


@pytest.fixture
def client():
    workdir = tempfile.mkdtemp()
    app = pyrogram.Client("dlkinds", api_id=1, api_hash="x", in_memory=True, workdir=workdir)
    app.me = SimpleNamespace(is_bot=False, is_premium=False, id=1)

    async def handle_download(packet):
        return os.path.join(str(packet[1]), packet[2])

    app.handle_download = handle_download
    app.test_workdir = workdir

    return app


async def test_a_paid_media_message_downloads_every_item(client):
    message = blank(types.Message)
    message.paid_media = types.PaidMediaInfo(
        stars_amount=5, media=[fake_media("one.bin"), fake_media("two.bin")]
    )

    result = await client.download_media(message)

    assert [os.path.basename(path) for path in result] == ["one.bin", "two.bin"]


async def test_a_paid_media_info_object_downloads_every_item(client):
    info = types.PaidMediaInfo(stars_amount=5, media=[fake_media("one.bin"), fake_media("two.bin")])

    result = await client.download_media(info)

    assert [os.path.basename(path) for path in result] == ["one.bin", "two.bin"]


async def test_a_named_paid_media_download_does_not_overwrite_itself(client):
    info = types.PaidMediaInfo(stars_amount=5, media=[fake_media("one.bin"), fake_media("two.bin")])

    result = await client.download_media(info, file_name="shot.jpg")

    assert [os.path.basename(path) for path in result] == ["shot_1.jpg", "shot_2.jpg"]


async def test_a_single_named_paid_media_download_keeps_the_name(client):
    info = types.PaidMediaInfo(stars_amount=5, media=[fake_media("one.bin")])

    result = await client.download_media(info, file_name="shot.jpg")

    assert [os.path.basename(path) for path in result] == ["shot.jpg"]


async def test_paid_media_that_was_not_bought_is_not_downloadable(client):
    preview = types.PaidMediaPreview(width=1, height=1, duration=None, thumbnail=None)
    message = blank(types.Message)
    message.paid_media = types.PaidMediaInfo(stars_amount=5, media=[preview])

    with pytest.raises(ValueError):
        await client.download_media(message)


async def test_a_story_message_downloads_the_story_media(client):
    story = blank(types.Story)
    story.photo = fake_media("story.jpg")
    story.media = enums.MessageMediaType.PHOTO

    message = blank(types.Message)
    message.story = story

    result = await client.download_media(message)

    assert os.path.basename(result) == "story.jpg"


async def test_a_replied_story_downloads_the_story_media(client):
    story = blank(types.Story)
    story.photo = fake_media("story.jpg")
    story.media = enums.MessageMediaType.PHOTO

    message = blank(types.Message)
    message.reply_to_story = story

    result = await client.download_media(message)

    assert os.path.basename(result) == "story.jpg"


async def test_a_story_object_downloads_directly(client):
    story = blank(types.Story)
    story.video = fake_media("story.mp4")
    story.media = enums.MessageMediaType.VIDEO

    result = await client.download_media(story)

    assert os.path.basename(result) == "story.mp4"


async def test_a_story_without_a_media_type_still_finds_its_media(client):
    story = blank(types.Story)
    story.video = fake_media("story.mp4")
    story.media = None

    result = await client.download_media(story)

    assert os.path.basename(result) == "story.mp4"


async def test_an_empty_story_is_not_downloadable(client):
    story = blank(types.Story)
    story.media = enums.MessageMediaType.PHOTO

    with pytest.raises(ValueError):
        await client.download_media(story)


async def test_a_stripped_thumbnail_expands_to_a_jpeg_in_memory(client):
    thumbnail = types.StrippedThumbnail(client=client, data=STRIPPED)

    result = await client.download_media(thumbnail, in_memory=True)

    assert bytes(result.getbuffer())[:2] == b"\xff\xd8"
    assert result.name.endswith(".jpg")


async def test_a_stripped_thumbnail_writes_a_jpeg_to_disk(client):
    thumbnail = types.StrippedThumbnail(client=client, data=STRIPPED)

    result = await client.download_media(thumbnail, file_name="thumb.jpg")

    assert os.path.basename(result) == "thumb.jpg"

    with open(result, "rb") as handle:
        assert handle.read(2) == b"\xff\xd8"


async def test_a_paid_media_preview_downloads_its_thumbnail(client):
    preview = types.PaidMediaPreview(
        width=1,
        height=1,
        duration=None,
        thumbnail=types.StrippedThumbnail(client=client, data=STRIPPED),
    )

    result = await client.download_media(preview, in_memory=True)

    assert bytes(result.getbuffer())[:2] == b"\xff\xd8"


async def test_a_preview_without_a_thumbnail_is_not_downloadable(client):
    preview = types.PaidMediaPreview(width=1, height=1, duration=None, thumbnail=None)

    with pytest.raises(ValueError):
        await client.download_media(preview, in_memory=True)


async def test_a_thumbnail_lands_inside_the_download_directory(client):
    thumbnail = types.StrippedThumbnail(client=client, data=STRIPPED)

    result = await client.download_media(thumbnail)

    assert os.path.abspath(result).startswith(os.path.abspath(client.test_workdir))


@pytest.mark.parametrize(
    "given, expected",
    [
        ("../../evil.jpg", "evil.jpg"),
        ("..\\..\\evil.jpg", "evil.jpg"),
        ("/etc/passwd", "passwd"),
        ("evil\x00.jpg", "evil.jpg"),
        ("..", ""),
        (".", ""),
        ("", ""),
        (None, ""),
        ("plain.jpg", "plain.jpg"),
    ],
)
def test_safe_file_name_strips_every_path_component(given, expected):
    from pyrogram.methods.messages.download_media import safe_file_name

    assert safe_file_name(given) == expected


async def test_a_chat_photo_downloads_the_big_file(client):
    photo = types.ChatPhoto(
        client=client,
        small_file_id=FILE_ID,
        small_photo_unique_id="s",
        big_file_id=FILE_ID,
        big_photo_unique_id="b",
        has_animation=False,
        is_personal=False,
    )

    result = await client.download_media(photo)

    assert os.path.basename(result).startswith("document_")


async def test_a_message_without_media_is_still_a_value_error(client):
    with pytest.raises(ValueError):
        await client.download_media(blank(types.Message))


async def test_a_file_name_from_the_server_cannot_escape_the_directory(client):
    result = await client.download_media(fake_media("../../evil.bin"))

    assert os.path.basename(result) == "evil.bin"


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


async def download_cdn_download(dc):
    client = make_e2e_client(dc, sessions=4)

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
    assert await download_cdn_download(CdnDC(SIZE, hash_span)) == SIZE


async def test_cdn_download_reuses_hashes_it_already_holds():
    per_chunk = CdnDC(SIZE, CHUNK)
    ahead = CdnDC(SIZE, SIZE)
    seeded = CdnDC(SIZE, SIZE, seed_hashes=True)

    assert await download_cdn_download(per_chunk) == SIZE
    assert await download_cdn_download(ahead) == SIZE
    assert await download_cdn_download(seeded) == SIZE

    assert per_chunk.hash_requests == SIZE // CHUNK
    assert ahead.hash_requests == 1
    assert seeded.hash_requests == 0


async def test_cdn_download_still_rejects_a_corrupted_chunk():
    with pytest.raises(CDNFileHashMismatch):
        await download_cdn_download(CdnDC(SIZE, SIZE, seed_hashes=True, corrupt_at=4 * CHUNK))


async def test_cdn_download_writes_every_chunk_to_disk(tmp_path):
    dc = CdnDC(SIZE, SIZE, seed_hashes=True)
    client = make_e2e_client(dc, sessions=4)

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


class CdnSessionFakeSession:
    MAX_RETRIES = 10

    def __init__(self, *args, **kwargs):
        self.auth_key = args[2]
        self.is_media = kwargs.get("is_media")
        self.is_cdn = kwargs.get("is_cdn")
        self.server_address = kwargs.get("server_address")
        self.port = kwargs.get("port")
        self.is_started = asyncio.Event()

    async def start(self, *args, **kwargs):
        self.is_started.set()

    async def invoke(self, *args, **kwargs):
        return None


class FakeAuth:
    def __init__(self, client, dc_id, test_mode, server_address=None, port=None):
        self.dc_id = dc_id
        self.server_address = server_address

    async def create(self):
        return b"cdn-key"


class CdnSessionFakeClient:
    get_session = pyrogram.Client.get_session

    def __init__(self):
        self.sessions = {}
        self.media_sessions = {}
        self._session_locks = {}
        self._session_creation_gate = asyncio.Semaphore(4)
        self.crypto_executor = None
        self.ipv6 = False
        self.business_connections = {}
        self.invoked = []

        class Storage:
            async def test_mode(self):
                return False

            async def dc_id(self):
                return 1

            async def auth_key(self):
                return b"home-key"

        self.storage = Storage()

    async def invoke(self, query, *args, **kwargs):
        self.invoked.append(type(query).__name__)
        await asyncio.sleep(0)
        return SimpleNamespace(id=1, bytes=b"exported")

    async def get_dc_option(self, dc_id, is_media=False, is_cdn=False, ipv6=False):
        return SimpleNamespace(ip_address=f"cdn{dc_id}.telegram", port=443)


async def _cdn_session(monkeypatch):
    monkeypatch.setattr(pyrogram.client, "Session", CdnSessionFakeSession)
    monkeypatch.setattr(pyrogram.client, "Auth", FakeAuth)

    client = CdnSessionFakeClient()
    session = await client.get_session(203, is_media=True, is_cdn=True, temporary=True)
    return client, session


async def test_cdn_session_is_marked_as_cdn(monkeypatch):
    _, session = await _cdn_session(monkeypatch)

    assert session.is_cdn is True
    assert session.is_media is True


async def test_cdn_session_uses_its_own_auth_key(monkeypatch):
    _, session = await _cdn_session(monkeypatch)

    assert session.auth_key == b"cdn-key"
    assert session.server_address == "cdn203.telegram"


async def test_cdn_session_does_not_import_authorization(monkeypatch):
    client, _ = await _cdn_session(monkeypatch)

    assert raw.functions.auth.ExportAuthorization.__name__ not in client.invoked


def test_cdn_redirect_carries_its_own_dc_id():
    assert "dc_id" in raw.types.upload.FileCdnRedirect.__slots__


def test_get_file_connects_to_the_redirected_dc():
    source = " ".join(inspect.getsource(pyrogram.Client.get_file).split())

    assert "cdn_session = await self.get_session( r.dc_id," in source


class MediaPoolFakeSession:
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
        return MediaPoolFakeSession()

    async def fake_make(dc_id, auth_key, server_address, port):
        created.append(dc_id)
        return MediaPoolFakeSession()

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
    import inspect

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


class MediaSessionPoolFakeSession:
    MAX_RETRIES = 10

    def __init__(self, *args, **kwargs):
        self.auth_key = args[2]
        self.server_address = kwargs.get("server_address")
        self.port = kwargs.get("port")
        self.is_started = asyncio.Event()

    async def start(self, *args, **kwargs):
        self.is_started.set()

    async def invoke(self, *args, **kwargs):
        return None


class MediaSessionPoolFakeAuth:
    def __init__(self, *args, **kwargs):
        pass

    async def create(self):
        return b"fresh-key"


class MediaSessionPoolFakeClient:
    _get_media_session_pool = pyrogram.Client._get_media_session_pool
    _make_media_session = pyrogram.Client._make_media_session

    def __init__(self):
        self.media_session_pools = {}
        self._media_sessions_locks = {}
        self._session_creation_gate = asyncio.Semaphore(4)
        self.crypto_executor = None
        self.exports = 0

        class Storage:
            async def test_mode(self):
                return False

            async def dc_id(self):
                return 1

            async def auth_key(self):
                return b"home-key"

        self.storage = Storage()

    async def invoke(self, query, *args, **kwargs):
        self.exports += 1
        await asyncio.sleep(0)
        return SimpleNamespace(id=1, bytes=b"exported")

    async def get_session(self, dc_id, is_media=False):
        self.exports += 1
        await asyncio.sleep(0)
        return MediaSessionPoolFakeSession(
            self,
            dc_id,
            b"authorized-key",
            False,
            server_address="media.dc",
            port=443,
        )


async def test_pool_exports_authorization_once(monkeypatch):
    monkeypatch.setattr(pyrogram.client, "Session", MediaSessionPoolFakeSession)
    monkeypatch.setattr(pyrogram.client, "Auth", MediaSessionPoolFakeAuth)

    client = MediaSessionPoolFakeClient()
    pools = await asyncio.gather(*(client._get_media_session_pool(2, 4) for _ in range(3)))

    assert client.exports == 1

    sessions = pools[0]
    assert len(sessions) == 4
    assert all(s.auth_key == b"authorized-key" for s in sessions)
    assert all(s.server_address == "media.dc" for s in sessions)
    assert all(p == sessions for p in pools)


async def test_pool_grows_without_re_exporting(monkeypatch):
    monkeypatch.setattr(pyrogram.client, "Session", MediaSessionPoolFakeSession)
    monkeypatch.setattr(pyrogram.client, "Auth", MediaSessionPoolFakeAuth)

    client = MediaSessionPoolFakeClient()
    small = await client._get_media_session_pool(2, 2)
    grown = await client._get_media_session_pool(2, 5)

    assert client.exports == 2
    assert len(grown) == 5
    assert grown[:2] == small


class FsPath:
    def __init__(self, path):
        self.path = path

    def __fspath__(self):
        return self.path


@pytest.fixture
def sample():
    directory = tempfile.mkdtemp()
    path = os.path.join(directory, "holiday.bin")

    with open(path, "wb") as handle:
        handle.write(b"payload")

    return path


def test_an_os_pathlike_keeps_its_real_name(sample):
    assert utils.get_file_name(FsPath(sample), fallback="file.zip") == "holiday.bin"


def test_a_pathlib_path_keeps_its_real_name(sample):
    assert utils.get_file_name(pathlib.Path(sample), fallback="file.zip") == "holiday.bin"


def test_a_string_path_keeps_its_real_name(sample):
    assert utils.get_file_name(sample, fallback="file.zip") == "holiday.bin"


def test_an_open_handle_does_not_send_its_directory(sample):
    with open(sample, "rb") as handle:
        name = utils.get_file_name(handle, fallback="file.zip")

    assert name == "holiday.bin"
    assert os.sep not in name
    assert "/" not in name


def test_a_named_buffer_is_reduced_to_its_base_name():
    buffer = io.BytesIO(b"payload")
    buffer.name = os.path.join("secret", "dir", "shared.bin")

    assert utils.get_file_name(buffer, fallback="file.zip") == "shared.bin"


def test_an_explicit_name_still_wins(sample):
    assert (
        utils.get_file_name(FsPath(sample), file_name="chosen.bin", fallback="file.zip")
        == "chosen.bin"
    )


@pytest.mark.parametrize("value", [b"raw", bytearray(b"raw"), 5, None, object()])
def test_something_that_is_not_a_file_falls_back(value):
    assert utils.get_file_name(value, fallback="file.zip") == "file.zip"


def test_a_nameless_buffer_falls_back():
    assert utils.get_file_name(io.BytesIO(b"payload"), fallback="file.zip") == "file.zip"


async def test_save_file_accepts_an_os_pathlike(sample):
    from types import SimpleNamespace

    import pyrogram

    client = pyrogram.Client("uploadkinds", api_id=1, api_hash="x", in_memory=True)
    client.me = SimpleNamespace(is_bot=False, is_premium=False, id=1)

    opened = {}

    async def get_pool(dc_id, n):
        opened["reached_upload"] = True
        raise RuntimeError("stop here")

    client._get_media_session_pool = get_pool

    with pytest.raises(Exception) as caught:
        await client.save_file(FsPath(sample))

    assert "Invalid file" not in str(caught.value)


async def test_save_file_still_refuses_bytes():
    from types import SimpleNamespace

    import pyrogram

    client = pyrogram.Client("uploadbytes", api_id=1, api_hash="x", in_memory=True)
    client.me = SimpleNamespace(is_bot=False, is_premium=False, id=1)

    with pytest.raises(ValueError, match="Invalid file"):
        await client.save_file(b"payload")
