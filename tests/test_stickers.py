from unittest.mock import Mock

import pytest

import pyrogram
from pyrogram import enums, raw, types, utils


def make_raw_sticker_set(
    title="My Pack",
    short_name="mypack_by_bot",
    count=1,
    animated=False,
    videos=False,
    emojis=False,
):
    mime_type = "image/webp"
    if animated:
        mime_type = "application/x-tgsticker"
    elif videos:
        mime_type = "video/webm"

    doc = raw.types.Document(
        id=101,
        access_hash=202,
        file_reference=b"ref",
        date=1700000000,
        mime_type=mime_type,
        size=1000,
        dc_id=1,
        attributes=[
            raw.types.DocumentAttributeSticker(
                alt="😀",
                stickerset=raw.types.InputStickerSetEmpty(),
            )
        ],
    )
    return raw.types.messages.StickerSet(
        set=raw.types.StickerSet(
            id=999,
            access_hash=888,
            title=title,
            short_name=short_name,
            count=count,
            hash=123,
            archived=False,
            official=False,
            masks=False,
            emojis=emojis,
            text_color=False,
            channel_emoji_status=False,
        ),
        packs=[],
        keywords=[],
        documents=[doc],
    )


class FakeStickersClient(pyrogram.Client):
    def __init__(self):
        self.sent_queries = []
        self.saved_files = []
        self.me = Mock(id=777, is_bot=True, username="mybot")
        self.fetch_stickers = False
        self.sticker_set_name_cache = utils.Cache(250)

    async def invoke(self, query, **kwargs):
        self.sent_queries.append(query)

        if isinstance(query, raw.functions.messages.UploadMedia):
            return raw.types.MessageMediaDocument(
                document=raw.types.Document(
                    id=101,
                    access_hash=202,
                    file_reference=b"ref",
                    date=1700000000,
                    mime_type="image/webp",
                    size=1000,
                    dc_id=1,
                    attributes=[
                        raw.types.DocumentAttributeSticker(
                            alt="😀",
                            stickerset=raw.types.InputStickerSetEmpty(),
                        )
                    ],
                )
            )

        if isinstance(
            query,
            (
                raw.functions.stickers.CreateStickerSet,
                raw.functions.stickers.AddStickerToSet,
                raw.functions.stickers.RemoveStickerFromSet,
                raw.functions.stickers.RenameStickerSet,
                raw.functions.stickers.SetStickerSetThumb,
                raw.functions.stickers.ReplaceSticker,
                raw.functions.stickers.ChangeSticker,
                raw.functions.stickers.ChangeStickerPosition,
                raw.functions.messages.GetStickerSet,
            ),
        ):
            title = getattr(query, "title", "My Pack")
            return make_raw_sticker_set(title=title)

        if isinstance(query, raw.functions.stickers.DeleteStickerSet):
            return True

        if isinstance(query, raw.functions.stickers.CheckShortName):
            return True

        if isinstance(query, raw.functions.stickers.SuggestShortName):
            return raw.types.stickers.SuggestedShortName(
                short_name=f"{query.title.lower()}_suggested"
            )

        if isinstance(query, raw.functions.messages.GetMyStickers):
            if query.offset_id != 0:
                return raw.types.messages.MyStickers(count=1, sets=[])
            sample = make_raw_sticker_set()
            covered = raw.types.StickerSetCovered(set=sample.set, cover=sample.documents[0])
            return raw.types.messages.MyStickers(count=1, sets=[covered])

        if isinstance(query, raw.functions.messages.InstallStickerSet):
            return raw.types.messages.StickerSetInstallResultSuccess()

        if isinstance(query, raw.functions.messages.UninstallStickerSet):
            return True

        return True

    async def resolve_peer(self, peer_id):
        return raw.types.InputPeerUser(user_id=777, access_hash=42)

    async def save_file(self, path, *args, **kwargs):
        if path is None:
            return None
        self.saved_files.append(str(path))
        return raw.types.InputFile(id=1, parts=1, name="sticker.webp", md5_checksum="")

    def guess_mime_type(self, path):
        return "image/webp"


@pytest.fixture
def client():
    return FakeStickersClient()


async def test_create_sticker_set_with_input_stickers(client):
    sticker_set = await client.create_sticker_set(
        user_id="me",
        title="Test Pack",
        short_name="test_pack_by_mybot",
        stickers=[
            types.InputSticker("sticker1.webp", emoji="😀", keywords="smile"),
            types.InputSticker("sticker2.webp", emoji="🎉"),
        ],
    )

    assert isinstance(sticker_set, types.StickerSet)
    assert sticker_set.id == 999
    assert sticker_set.title == "Test Pack"
    assert sticker_set.short_name == "mypack_by_bot"
    assert len(sticker_set.stickers) == 1

    create_query = next(
        q for q in client.sent_queries if isinstance(q, raw.functions.stickers.CreateStickerSet)
    )
    assert create_query.title == "Test Pack"
    assert create_query.short_name == "test_pack_by_mybot"
    assert len(create_query.stickers) == 2
    assert create_query.stickers[0].emoji == "😀"
    assert create_query.stickers[0].keywords == "smile"
    assert create_query.stickers[1].emoji == "🎉"


async def test_create_sticker_set_with_strings(client):
    sticker_set = await client.create_sticker_set(
        user_id="me",
        title="String Pack",
        short_name="string_pack_by_mybot",
        stickers=["sticker1.webp"],
        default_emoji="🔥",
    )

    assert isinstance(sticker_set, types.StickerSet)
    create_query = next(
        q for q in client.sent_queries if isinstance(q, raw.functions.stickers.CreateStickerSet)
    )
    assert create_query.stickers[0].emoji == "🔥"


async def test_add_sticker_to_set(client):
    sticker_set = await client.add_sticker_to_set(
        short_name="mypack_by_bot",
        sticker="sticker3.webp",
        emoji="🚀",
        keywords="space",
    )

    assert isinstance(sticker_set, types.StickerSet)
    add_query = next(
        q for q in client.sent_queries if isinstance(q, raw.functions.stickers.AddStickerToSet)
    )
    assert isinstance(add_query.stickerset, raw.types.InputStickerSetShortName)
    assert add_query.stickerset.short_name == "mypack_by_bot"
    assert add_query.sticker.emoji == "🚀"
    assert add_query.sticker.keywords == "space"


async def test_remove_sticker_from_set(client):
    raw_doc = raw.types.InputDocument(id=101, access_hash=202, file_reference=b"ref")
    sticker_set = await client.remove_sticker_from_set(sticker=raw_doc)

    assert isinstance(sticker_set, types.StickerSet)
    remove_query = next(
        q for q in client.sent_queries if isinstance(q, raw.functions.stickers.RemoveStickerFromSet)
    )
    assert remove_query.sticker.id == 101


async def test_delete_sticker_set(client):
    result = await client.delete_sticker_set("mypack_by_bot")

    assert result is True
    delete_query = next(
        q for q in client.sent_queries if isinstance(q, raw.functions.stickers.DeleteStickerSet)
    )
    assert delete_query.stickerset.short_name == "mypack_by_bot"


async def test_set_sticker_set_title(client):
    sticker_set = await client.set_sticker_set_title("mypack_by_bot", "Updated Title")

    assert isinstance(sticker_set, types.StickerSet)
    rename_query = next(
        q for q in client.sent_queries if isinstance(q, raw.functions.stickers.RenameStickerSet)
    )
    assert rename_query.title == "Updated Title"
    assert rename_query.stickerset.short_name == "mypack_by_bot"


async def test_set_sticker_set_thumb(client):
    sticker_set = await client.set_sticker_set_thumb("mypack_by_bot", thumb="thumb.webp")

    assert isinstance(sticker_set, types.StickerSet)
    thumb_query = next(
        q for q in client.sent_queries if isinstance(q, raw.functions.stickers.SetStickerSetThumb)
    )
    assert thumb_query.stickerset.short_name == "mypack_by_bot"
    assert thumb_query.thumb.id == 101


async def test_get_sticker_set(client):
    sticker_set = await client.get_sticker_set("mypack_by_bot")

    assert isinstance(sticker_set, types.StickerSet)
    assert sticker_set.short_name == "mypack_by_bot"
    assert sticker_set.count == 1
    assert len(sticker_set.stickers) == 1
    assert sticker_set.is_animated is False
    assert sticker_set.is_video is False


async def test_check_sticker_set_name(client):
    assert await client.check_sticker_set_name("available_pack") is True
    check_query = next(
        q for q in client.sent_queries if isinstance(q, raw.functions.stickers.CheckShortName)
    )
    assert check_query.short_name == "available_pack"


async def test_create_custom_emoji_sticker_set(client):
    await client.create_sticker_set(
        user_id="me",
        title="Emoji Pack",
        short_name="emoji_pack_by_mybot",
        stickers=["emoji.webp"],
        emojis=True,
        text_color=True,
    )

    create_query = next(
        q
        for q in reversed(client.sent_queries)
        if isinstance(q, raw.functions.stickers.CreateStickerSet)
    )
    assert create_query.emojis is True
    assert create_query.text_color is True


async def test_create_mask_sticker_set(client):
    await client.create_sticker_set(
        user_id="me",
        title="Mask Pack",
        short_name="mask_pack_by_mybot",
        stickers=["mask.webp"],
        masks=True,
    )

    create_query = next(
        q
        for q in reversed(client.sent_queries)
        if isinstance(q, raw.functions.stickers.CreateStickerSet)
    )
    assert create_query.masks is True


def test_input_sticker_attributes():
    stk = types.InputSticker(
        sticker="cat.webp",
        emoji="🐱",
        keywords="cat, kitten",
    )
    assert stk.sticker == "cat.webp"
    assert stk.emoji == "🐱"
    assert stk.keywords == "cat, kitten"
    assert stk.mask_coords is None


async def test_animated_stickerset_detection(client):
    raw_set = make_raw_sticker_set(animated=True)
    parsed = await types.StickerSet._parse(client, raw_set)
    assert parsed.is_animated is True
    assert parsed.is_video is False


async def test_video_stickerset_detection(client):
    raw_set = make_raw_sticker_set(videos=True)
    parsed = await types.StickerSet._parse(client, raw_set)
    assert parsed.is_video is True
    assert parsed.is_animated is False


async def test_invalid_stickerset_raises():
    from pyrogram.methods.stickers.resolve import resolve_stickerset

    with pytest.raises(ValueError, match="Invalid sticker set identifier"):
        resolve_stickerset(12345)


async def test_get_stickers(client):
    stickers = await client.get_stickers("mypack_by_bot")
    assert isinstance(stickers, list)
    assert len(stickers) == 1
    assert isinstance(stickers[0], types.Sticker)


async def test_get_custom_emoji_stickers(client):
    doc = raw.types.Document(
        id=101,
        access_hash=202,
        file_reference=b"ref",
        date=1700000000,
        mime_type="image/webp",
        size=1000,
        dc_id=1,
        attributes=[
            raw.types.DocumentAttributeCustomEmoji(
                free=True,
                text_color=False,
                alt="⭐",
                stickerset=raw.types.InputStickerSetEmpty(),
            )
        ],
    )

    orig_invoke = client.invoke

    async def mock_invoke(query, **kwargs):
        if isinstance(query, raw.functions.messages.GetCustomEmojiDocuments):
            return [doc]
        return await orig_invoke(query, **kwargs)

    client.invoke = mock_invoke

    emojis = await client.get_custom_emoji_stickers([101])
    assert isinstance(emojis, list)
    assert len(emojis) == 1
    assert emojis[0].custom_emoji_id == "101"


async def test_mask_position_conversion(client):
    mask_pos = types.MaskPosition(
        point=pyrogram.enums.MaskPointType.FOREHEAD,
        x_shift=0.5,
        y_shift=1.0,
        scale=2.0,
    )
    stk = types.InputSticker(
        sticker="mask.webp",
        emoji="🎭",
        mask_coords=mask_pos,
    )

    await client.create_sticker_set(
        user_id="me",
        title="Masks",
        short_name="masks_by_mybot",
        stickers=[stk],
        masks=True,
    )

    create_query = next(
        q
        for q in reversed(client.sent_queries)
        if isinstance(q, raw.functions.stickers.CreateStickerSet)
    )
    assert create_query.stickers[0].mask_coords.n == 0
    assert create_query.stickers[0].mask_coords.x == 0.5
    assert create_query.stickers[0].mask_coords.y == 1.0
    assert create_query.stickers[0].mask_coords.zoom == 2.0


async def test_add_sticker_from_existing_sticker(client):
    # Simulating a sticker object received in a message (types.Sticker)
    existing_sticker = types.Sticker(
        file_id="CAACAgIAAxkBAAI",
        file_unique_id="unique_123",
        type=pyrogram.enums.StickerType.REGULAR,
        width=512,
        height=512,
        is_animated=False,
        is_video=False,
        emoji="🔥",
    )

    # 1. Directly passing existing_sticker to add_sticker_to_set
    await client.add_sticker_to_set(
        short_name="my_pack",
        sticker=existing_sticker,
    )
    add_query = next(
        q
        for q in reversed(client.sent_queries)
        if isinstance(q, raw.functions.stickers.AddStickerToSet)
    )
    assert add_query.sticker.emoji == "🔥"

    # 2. Wrapping existing_sticker in InputSticker without specifying emoji
    input_stk = types.InputSticker(sticker=existing_sticker)
    assert input_stk.emoji == "🔥"


async def test_replace_sticker(client):
    old_sticker = types.Sticker(
        file_id="CAACAgIAAxkBAAI",
        file_unique_id="unique_123",
        type=pyrogram.enums.StickerType.REGULAR,
        width=512,
        height=512,
        is_animated=False,
        is_video=False,
        emoji="🔥",
    )

    res = await client.replace_sticker(
        sticker=old_sticker,
        new_sticker="new_sticker.webp",
        emoji="🚀",
        keywords="rocket, space",
    )
    assert isinstance(res, types.StickerSet)

    replace_query = next(
        q
        for q in reversed(client.sent_queries)
        if isinstance(q, raw.functions.stickers.ReplaceSticker)
    )
    assert replace_query.new_sticker.emoji == "🚀"
    assert replace_query.new_sticker.keywords == "rocket, space"


async def test_change_sticker(client):
    mask_pos = types.MaskPosition(
        point=pyrogram.enums.MaskPointType.FOREHEAD,
        x_shift=0.2,
        y_shift=0.3,
        scale=1.5,
    )

    res = await client.change_sticker(
        sticker="CAACAgIAAxkBAAI",
        emoji="🌟",
        keywords="star, shiny",
        mask_coords=mask_pos,
    )
    assert isinstance(res, types.StickerSet)

    change_query = next(
        q
        for q in reversed(client.sent_queries)
        if isinstance(q, raw.functions.stickers.ChangeSticker)
    )
    assert change_query.emoji == "🌟"
    assert change_query.keywords == "star, shiny"
    assert change_query.mask_coords.x == 0.2


async def test_set_sticker_position(client):
    res = await client.set_sticker_position(
        sticker="CAACAgIAAxkBAAI",
        position=2,
    )
    assert isinstance(res, types.StickerSet)

    pos_query = next(
        q
        for q in reversed(client.sent_queries)
        if isinstance(q, raw.functions.stickers.ChangeStickerPosition)
    )
    assert pos_query.position == 2


async def test_suggest_sticker_set_name(client):
    suggested = await client.suggest_sticker_set_name("Cool Cats")
    assert suggested == "cool cats_suggested"


async def test_get_my_stickers(client):
    sets = []
    async for s in client.get_my_stickers(limit=5):
        sets.append(s)

    assert len(sets) == 1
    assert isinstance(sets[0], types.StickerSet)
    assert sets[0].title == "My Pack"


async def test_save_and_unsave_sticker_set(client):
    # Test primary methods
    res_save = await client.save_sticker_set("animals")
    assert res_save is True

    save_query = next(
        q
        for q in reversed(client.sent_queries)
        if isinstance(q, raw.functions.messages.InstallStickerSet)
    )
    assert save_query.archived is False

    res_unsave = await client.unsave_sticker_set("animals")
    assert res_unsave is True

    unsave_query = next(
        q
        for q in reversed(client.sent_queries)
        if isinstance(q, raw.functions.messages.UninstallStickerSet)
    )
    assert unsave_query.stickerset.short_name == "animals"


async def test_all_sticker_method_aliases(client):
    raw_doc = raw.types.InputDocument(id=101, access_hash=202, file_reference=b"ref")

    # create_new_sticker_set
    res = await client.create_new_sticker_set(
        user_id="me", title="New Pack", short_name="new_pack_by_bot", stickers=["sticker.webp"]
    )
    assert isinstance(res, types.StickerSet)

    # delete_sticker_from_set
    res = await client.delete_sticker_from_set(raw_doc)
    assert isinstance(res, types.StickerSet)

    # replace_sticker_in_set
    res = await client.replace_sticker_in_set(raw_doc, "new.webp", emoji="🌟")
    assert isinstance(res, types.StickerSet)

    # set_sticker_emoji_list with list and str
    res = await client.set_sticker_emoji_list(raw_doc, ["🎉", "🥳"])
    assert isinstance(res, types.StickerSet)
    change_query = next(
        q
        for q in reversed(client.sent_queries)
        if isinstance(q, raw.functions.stickers.ChangeSticker)
    )
    assert change_query.emoji == "🎉🥳"

    # set_sticker_keywords with list and str
    res = await client.set_sticker_keywords(raw_doc, ["party", "fun"])
    assert isinstance(res, types.StickerSet)
    change_query = next(
        q
        for q in reversed(client.sent_queries)
        if isinstance(q, raw.functions.stickers.ChangeSticker)
    )
    assert change_query.keywords == "party,fun"

    # set_sticker_mask_position
    res = await client.set_sticker_mask_position(
        raw_doc,
        types.MaskPosition(point=enums.MaskPointType.FOREHEAD, x_shift=0.1, y_shift=0.2, scale=1.0),
    )
    assert isinstance(res, types.StickerSet)

    # set_sticker_position_in_set
    res = await client.set_sticker_position_in_set(raw_doc, 1)
    assert isinstance(res, types.StickerSet)

    # set_sticker_set_thumbnail
    res = await client.set_sticker_set_thumbnail("mypack_by_bot", thumb="thumb.webp")
    assert isinstance(res, types.StickerSet)

    # set_custom_emoji_sticker_set_thumbnail
    res = await client.set_custom_emoji_sticker_set_thumbnail("mypack_by_bot", 12345)
    assert isinstance(res, types.StickerSet)

    # get_suggested_sticker_set_name
    suggested = await client.get_suggested_sticker_set_name("Cool Cats")
    assert suggested == "cool cats_suggested"

    # get_owned_sticker_sets
    owned = []
    async for s in client.get_owned_sticker_sets():
        owned.append(s)
    assert len(owned) == 1

    # add_favorite_sticker & remove_favorite_sticker
    assert await client.add_favorite_sticker(raw_doc) is True
    assert await client.remove_favorite_sticker(raw_doc) is True

    # add_recent_sticker & remove_recent_sticker & clear_recent_stickers
    assert await client.add_recent_sticker(raw_doc) is True
    assert await client.remove_recent_sticker(raw_doc) is True
    assert await client.clear_recent_stickers() is True


async def test_sticker_set_name_cache(client):
    cache = utils.Cache(3)
    cache.set((1, 100), "pack_one")
    cache.set((2, 200), "pack_two")
    assert cache.get((1, 100)) == "pack_one"
    assert cache.get((3, 300)) is None
    assert len(cache) == 2

    # LRU eviction
    cache.set((3, 300), "pack_three")
    cache.set((4, 400), "pack_four")
    assert len(cache) == 3
    # pack_two was oldest accessed because pack_one was accessed right before
    assert cache.get((2, 200)) is None
    assert cache.get((1, 100)) == "pack_one"
