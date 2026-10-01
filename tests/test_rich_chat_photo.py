from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
import pyrogram
import pytest
from pyrogram import enums, raw, types


@pytest.mark.asyncio
async def test_chat_photo_user_profile_photo_fallback():
    raw_photo = raw.types.UserProfilePhoto(
        photo_id=123456789,
        dc_id=2,
        has_video=True,
        personal=False,
    )
    # Sync _parse: works for UserProfilePhoto
    chat_photo = types.ChatPhoto._parse(None, raw_photo)
    assert chat_photo is not None
    assert chat_photo.has_animation is True
    assert chat_photo.is_personal is False
    assert chat_photo.animation is None
    assert chat_photo.sticker is None
    assert chat_photo.added_date is None


@pytest.mark.asyncio
async def test_chat_photo_rich_raw_photo_with_animation_and_sticker():
    sticker_markup = raw.types.VideoSizeStickerMarkup(
        stickerset=raw.types.InputStickerSetShortName(short_name="PremiumGifts"),
        sticker_id=5717737768998666247,
        background_colors=[0xFFFFFF],
    )
    video_size = raw.types.VideoSize(
        type="u",
        w=800,
        h=800,
        size=317688,
        video_start_ts=0.0,
    )
    photo_size = raw.types.PhotoSize(
        type="a",
        w=800,
        h=800,
        size=1024,
    )
    raw_photo = raw.types.Photo(
        id=987654321,
        access_hash=123456,
        file_reference=b"fileref",
        date=1783421063,
        sizes=[photo_size],
        video_sizes=[video_size, sticker_markup],
        dc_id=2,
        has_stickers=True,
    )

    chat_photo = await types.ChatPhoto._parse_full(None, raw_photo)
    assert chat_photo is not None
    assert chat_photo.has_animation is True
    assert chat_photo.added_date == datetime.fromtimestamp(1783421063)
    assert chat_photo.animation is not None
    assert chat_photo.animation.length == 800
    assert chat_photo.animation.animation is not None
    assert chat_photo.animation.animation.width == 800
    assert chat_photo.animation.animation.height == 800
    assert chat_photo.animation.animation.file_size == 317688

    assert chat_photo.sticker is not None
    assert chat_photo.sticker.type == enums.ChatPhotoStickerType.REGULAR_OR_MASK
    assert chat_photo.sticker.set_name == "PremiumGifts"
    assert chat_photo.sticker.sticker_id == 5717737768998666247


@pytest.mark.asyncio
async def test_chat_photo_rich_raw_photo_with_input_stickerset_id():
    client = MagicMock(spec=pyrogram.Client)
    mock_messages_stickerset = MagicMock()
    mock_messages_stickerset.set.short_name = "RealStickerSetName"
    client.invoke = AsyncMock(return_value=mock_messages_stickerset)

    sticker_markup = raw.types.VideoSizeStickerMarkup(
        stickerset=raw.types.InputStickerSetID(id=328917524764688479, access_hash=99887766),
        sticker_id=5717737768998666247,
        background_colors=[0xFFFFFF],
    )
    raw_photo = raw.types.Photo(
        id=987654321,
        access_hash=123456,
        file_reference=b"fileref",
        date=1783421063,
        sizes=[raw.types.PhotoSize(type="a", w=800, h=800, size=1024)],
        video_sizes=[sticker_markup],
        dc_id=2,
        has_stickers=True,
    )

    # Sync _parse: no sticker resolved (sticker is None for sync path)
    sync_photo = types.ChatPhoto._parse(client, raw_photo)
    assert sync_photo is not None
    assert sync_photo.sticker is None

    # Async _parse_full resolves the real name from Telegram API
    chat_photo = await types.ChatPhoto._parse_full(client, raw_photo)
    assert chat_photo is not None
    assert chat_photo.sticker is not None
    assert chat_photo.sticker.type == enums.ChatPhotoStickerType.REGULAR_OR_MASK
    assert chat_photo.sticker.set_name == "RealStickerSetName"
    assert chat_photo.sticker.sticker_id == 5717737768998666247


@pytest.mark.asyncio
async def test_chat_photo_rich_raw_photo_with_custom_emoji():
    emoji_markup = raw.types.VideoSizeEmojiMarkup(
        emoji_id=1122334455,
        background_colors=[0x000000],
    )
    raw_photo = raw.types.Photo(
        id=987654322,
        access_hash=654321,
        file_reference=b"fileref2",
        date=1783421000,
        sizes=[raw.types.PhotoSize(type="a", w=320, h=320, size=512)],
        video_sizes=[emoji_markup],
        dc_id=2,
    )

    # Custom emoji sticker is resolved via _parse_full (async path)
    chat_photo = await types.ChatPhoto._parse_full(None, raw_photo)
    assert chat_photo is not None
    assert chat_photo.sticker is not None
    assert chat_photo.sticker.type == enums.ChatPhotoStickerType.CUSTOM_EMOJI
    assert chat_photo.sticker.custom_emoji_id == "1122334455"
