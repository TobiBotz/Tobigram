import io
import sys
from pathlib import Path

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


class FakeStickerClient:
    def __init__(self, invoke_return=None, invoke_exc=None):
        self.sticker_set_name_cache = None
        self.fetch_stickers = False
        self.invoked = []
        self.invoke_return = invoke_return
        self.invoke_exc = invoke_exc

    async def invoke(self, query):
        self.invoked.append(query)
        if self.invoke_exc:
            raise self.invoke_exc
        return self.invoke_return

    async def resolve_peer(self, peer_id):
        return raw.types.InputPeerSelf()


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

    client = FakeStickerClient(
        invoke_return=raw.types.messages.StickerSet(
            set=raw_set(12345, "sync_pack"),
            packs=[],
            keywords=[],
            documents=[],
        )
    )
    client.sticker_set_name_cache = utils.Cache(10)

    # First call: cache miss, invokes client.invoke
    name = await types.Sticker._get_sticker_set_name(client, (12345, 1))
    assert name == "sync_pack"
    assert len(client.invoked) == 1
    assert client.sticker_set_name_cache.get((12345, 1)) == "sync_pack"
    assert types.Sticker.cache.get((12345, 1)) == "sync_pack"

    # Second call: cache hit in client.sticker_set_name_cache & Sticker.cache
    name2 = await types.Sticker._get_sticker_set_name(client, (12345, 1))
    assert name2 == "sync_pack"
    assert len(client.invoked) == 1

    # Clear Sticker.cache to ensure it also reads from client.sticker_set_name_cache directly
    types.Sticker.cache.clear()
    name3 = await types.Sticker._get_sticker_set_name(client, (12345, 1))
    assert name3 == "sync_pack"
    assert len(client.invoked) == 1


@pytest.mark.asyncio
async def test_get_sticker_set_name_with_async_cache():
    types.Sticker.cache.clear()

    async_store = {}

    class AsyncCache:
        async def get(self, key):
            return async_store.get(key)

        async def set(self, key, value):
            async_store[key] = value

    client = FakeStickerClient(
        invoke_return=raw.types.messages.StickerSet(
            set=raw_set(54321, "async_pack"),
            packs=[],
            keywords=[],
            documents=[],
        )
    )
    client.sticker_set_name_cache = AsyncCache()

    # Cache miss
    name = await types.Sticker._get_sticker_set_name(client, (54321, 1))
    assert name == "async_pack"
    assert async_store[(54321, 1)] == "async_pack"
    assert len(client.invoked) == 1

    # Cache hit
    types.Sticker.cache.clear()
    name2 = await types.Sticker._get_sticker_set_name(client, (54321, 1))
    assert name2 == "async_pack"
    assert len(client.invoked) == 1


@pytest.mark.asyncio
async def test_get_sticker_set_name_invalid_set():
    types.Sticker.cache.clear()
    client = FakeStickerClient(invoke_exc=StickersetInvalid())
    client.sticker_set_name_cache = utils.Cache(10)

    name = await types.Sticker._get_sticker_set_name(client, (99999, 1))
    assert name is None


@pytest.mark.asyncio
async def test_sticker_parse_with_cache_miss():
    types.Sticker.cache.clear()
    client = FakeStickerClient(
        invoke_return=raw.types.messages.StickerSet(
            set=raw_set(777, "parse_pack"),
            packs=[],
            keywords=[],
            documents=[],
        )
    )
    client.fetch_stickers = True
    client.sticker_set_name_cache = utils.Cache(10)

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
        client,
        doc,
        {type(a): a for a in doc.attributes},
    )

    assert sticker.set_name == "parse_pack"
    assert sticker.emoji == "😊"
    assert client.sticker_set_name_cache.get((777, 1)) == "parse_pack"


@pytest.mark.asyncio
async def test_sticker_parse_short_name():
    doc = raw.types.Document(
        id=10102,
        access_hash=20203,
        file_reference=b"ref",
        date=1700000000,
        mime_type="image/webp",
        size=1024,
        dc_id=1,
        attributes=[
            raw.types.DocumentAttributeSticker(
                alt="🔥",
                stickerset=raw.types.InputStickerSetShortName(short_name="fire_pack"),
            ),
        ],
    )

    sticker = await types.Sticker._parse(
        None,
        doc,
        {type(a): a for a in doc.attributes},
    )

    assert sticker.set_name == "fire_pack"
    assert sticker.emoji == "🔥"


@pytest.mark.asyncio
async def test_sticker_parse_video_thumbs_without_video_size():
    doc = raw.types.Document(
        id=10103,
        access_hash=20204,
        file_reference=b"ref",
        date=1700000000,
        mime_type="image/webp",
        size=1024,
        dc_id=1,
        attributes=[
            raw.types.DocumentAttributeSticker(
                alt="🎉",
                stickerset=raw.types.InputStickerSetShortName(short_name="party"),
            ),
        ],
        video_thumbs=[
            raw.types.VideoSizeEmojiMarkup(emoji_id=123, background_colors=[0]),
        ],
    )

    sticker = await types.Sticker._parse(
        None,
        doc,
        {type(a): a for a in doc.attributes},
    )

    assert sticker is not None
    assert sticker.premium_animation is None
    assert sticker.set_name == "party"


@pytest.mark.asyncio
async def test_create_new_sticker_set_passes_input_user():
    client = FakeStickerClient(
        invoke_return=raw.types.messages.StickerSet(
            set=raw_set(888, "created_pack"),
            packs=[],
            keywords=[],
            documents=[],
        )
    )

    res = await pyrogram.Client.create_new_sticker_set(
        client,
        user_id="me",
        name="created_pack",
        title="Created Pack",
        stickers=[],
    )

    assert res.name == "created_pack"
    assert len(client.invoked) == 1
    called_call = client.invoked[0]
    assert isinstance(called_call, raw.functions.stickers.CreateStickerSet)
    assert isinstance(called_call.user_id, raw.types.InputUserSelf)


@pytest.mark.asyncio
async def test_sticker_set_parse_covered_and_document_empty():
    valid_doc = raw.types.Document(
        id=99901,
        access_hash=123,
        file_reference=b"ref",
        date=1700000000,
        mime_type="image/webp",
        size=100,
        dc_id=1,
        attributes=[
            raw.types.DocumentAttributeSticker(
                alt="⭐", stickerset=raw.types.InputStickerSetEmpty()
            )
        ],
    )
    empty_doc = raw.types.DocumentEmpty(id=99902)

    covered = raw.types.StickerSetCovered(
        set=raw_set(555, "covered_pack"),
        cover=valid_doc,
    )

    parsed = await types.StickerSet._parse(None, covered)
    assert parsed.name == "covered_pack"
    assert len(parsed.stickers) == 1
    assert parsed.stickers[0].emoji == "⭐"

    # With empty_doc in messages.StickerSet documents
    msg_set = raw.types.messages.StickerSet(
        set=raw_set(556, "mixed_pack"),
        packs=[],
        keywords=[],
        documents=[valid_doc, empty_doc],
    )
    parsed_mixed = await types.StickerSet._parse(None, msg_set)
    assert parsed_mixed.name == "mixed_pack"
    assert len(parsed_mixed.stickers) == 1
