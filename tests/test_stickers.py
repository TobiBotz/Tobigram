import io
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pyrogram
from pyrogram import enums, raw, types, utils
from pyrogram.errors import StickersetInvalid
from pyrogram.types.input_content import input_sticker


def raw_set(set_id, name="set"):
    return raw.types.StickerSet(
        id=set_id,
        access_hash=1,
        title=name,
        short_name=name,
        count=0,
        hash=0,
    )


class OwnedClient:
    def __init__(self, pages):
        self.pages = pages
        self.sent = []

    async def invoke(self, query):
        self.sent.append(query)
        page = self.pages[min(len(self.sent), len(self.pages)) - 1]

        return raw.types.messages.MyStickers(
            count=page[0],
            sets=[raw.types.StickerSetNoCovered(set=raw_set(i, f"s{i}")) for i in page[1]],
        )


async def owned(client, **kwargs):
    return [s.id async for s in pyrogram.Client.get_owned_sticker_sets(client, **kwargs)]


@pytest.mark.asyncio
async def test_owned_sets_stop_when_telegram_repeats_the_page():
    client = OwnedClient([(250, list(range(100)))])

    assert await owned(client) == list(range(100))
    assert len(client.sent) == 2


@pytest.mark.asyncio
async def test_owned_sets_page_forward_and_stop_at_the_count():
    client = OwnedClient([(3, [1, 2]), (3, [2, 3]), (3, [3])])

    assert await owned(client, limit=0) == [1, 2]

    client = OwnedClient(
        [(250, list(range(100))), (250, list(range(100, 200))), (250, list(range(200, 250)))]
    )

    assert await owned(client) == list(range(250))
    assert len(client.sent) == 3


@pytest.mark.asyncio
async def test_a_set_without_stickers_parses():
    sticker_set = await types.StickerSet._parse(
        None,
        raw.types.messages.StickerSet(set=raw_set(9, "empty"), packs=[], keywords=[], documents=[]),
    )

    assert sticker_set.stickers == []
    assert sticker_set.thumbs is None
    assert sticker_set.link == "https://t.me/addstickers/empty"


def test_mask_position_writes_back_what_it_read():
    coords = raw.types.MaskCoords(n=2, x=0.5, y=-1.0, zoom=2.0)
    written = types.MaskPosition._parse(coords).write()

    assert (written.n, written.x, written.y, written.zoom) == (2, 0.5, -1.0, 2.0)


def test_urls_and_files_are_uploaded_and_anything_else_is_a_file_id(tmp_path):
    local = tmp_path / "s.png"
    local.write_bytes(b"x")

    def sticker(value):
        return types.InputSticker(value, enums.StickerFormat.STATIC, ["👍"])

    assert sticker("https://example.com/s.png")._is_upload()
    assert sticker(str(local))._is_upload()
    assert sticker(io.BytesIO(b"x"))._is_upload()
    assert not sticker("CAACAgQAAx")._is_upload()
    assert not sticker("ftp://example.com/s.png")._is_url()


def test_a_download_over_the_cap_is_refused(monkeypatch):
    class Response(io.BytesIO):
        def __enter__(self):
            return self

        def __exit__(self, *args):
            self.close()

    monkeypatch.setattr(input_sticker, "MAX_DOWNLOAD_SIZE", 4)
    monkeypatch.setattr(input_sticker.urllib.request, "urlopen", lambda *a, **k: Response(b"12345"))

    with pytest.raises(ValueError):
        types.InputSticker._download("https://example.com/s.png")

    monkeypatch.setattr(input_sticker.urllib.request, "urlopen", lambda *a, **k: Response(b"1234"))

    assert types.InputSticker._download("https://example.com/s.png") == b"1234"


@pytest.mark.asyncio
async def test_get_sticker_set_name_with_sync_cache():
    types.Sticker.cache.clear()

    mock_client = MagicMock()
    mock_client.sticker_set_name_cache = utils.Cache(10)
    mock_client.invoke = AsyncMock(
        return_value=raw.types.messages.StickerSet(
            set=raw_set(12345, "sync_pack"),
            packs=[],
            keywords=[],
            documents=[],
        )
    )

    # First call: cache miss, invokes client.invoke
    name = await types.Sticker._get_sticker_set_name(mock_client, (12345, 1))
    assert name == "sync_pack"
    assert mock_client.invoke.await_count == 1
    assert mock_client.sticker_set_name_cache.get((12345, 1)) == "sync_pack"
    assert types.Sticker.cache.get((12345, 1)) == "sync_pack"

    # Second call: cache hit in client.sticker_set_name_cache & Sticker.cache
    name2 = await types.Sticker._get_sticker_set_name(mock_client, (12345, 1))
    assert name2 == "sync_pack"
    assert mock_client.invoke.await_count == 1

    # Clear Sticker.cache to ensure it also reads from client.sticker_set_name_cache directly
    types.Sticker.cache.clear()
    name3 = await types.Sticker._get_sticker_set_name(mock_client, (12345, 1))
    assert name3 == "sync_pack"
    assert mock_client.invoke.await_count == 1


@pytest.mark.asyncio
async def test_get_sticker_set_name_with_async_cache():
    types.Sticker.cache.clear()

    async_store = {}

    class AsyncCache:
        async def get(self, key):
            return async_store.get(key)

        async def set(self, key, value):
            async_store[key] = value

    mock_client = MagicMock()
    mock_client.sticker_set_name_cache = AsyncCache()
    mock_client.invoke = AsyncMock(
        return_value=raw.types.messages.StickerSet(
            set=raw_set(54321, "async_pack"),
            packs=[],
            keywords=[],
            documents=[],
        )
    )

    # Cache miss
    name = await types.Sticker._get_sticker_set_name(mock_client, (54321, 1))
    assert name == "async_pack"
    assert async_store[(54321, 1)] == "async_pack"
    assert mock_client.invoke.await_count == 1

    # Cache hit
    types.Sticker.cache.clear()
    name2 = await types.Sticker._get_sticker_set_name(mock_client, (54321, 1))
    assert name2 == "async_pack"
    assert mock_client.invoke.await_count == 1


@pytest.mark.asyncio
async def test_get_sticker_set_name_invalid_set():
    types.Sticker.cache.clear()
    mock_client = MagicMock()
    mock_client.sticker_set_name_cache = utils.Cache(10)
    mock_client.invoke = AsyncMock(side_effect=StickersetInvalid())

    name = await types.Sticker._get_sticker_set_name(mock_client, (99999, 1))
    assert name is None


@pytest.mark.asyncio
async def test_sticker_parse_with_cache_miss():
    types.Sticker.cache.clear()
    mock_client = MagicMock()
    mock_client.fetch_stickers = True
    mock_client.sticker_set_name_cache = utils.Cache(10)
    mock_client.invoke = AsyncMock(
        return_value=raw.types.messages.StickerSet(
            set=raw_set(777, "parse_pack"),
            packs=[],
            keywords=[],
            documents=[],
        )
    )

    doc = raw.types.Document(
        id=10101,
        access_hash=20202,
        file_reference=b"ref",
        date=1700000000,
        mime_type="image/webp",
        size=1024,
        dc_id=1,
        attributes=[
            raw.types.DocumentAttributeSticker(
                alt="😊",
                stickerset=raw.types.InputStickerSetID(id=777, access_hash=1),
            ),
            raw.types.DocumentAttributeImageSize(w=512, h=512),
        ],
    )

    sticker = await types.Sticker._parse(
        mock_client,
        doc,
        {type(a): a for a in doc.attributes},
    )

    assert sticker.set_name == "parse_pack"
    assert sticker.emoji == "😊"
    assert mock_client.sticker_set_name_cache.get((777, 1)) == "parse_pack"
