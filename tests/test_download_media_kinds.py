import os
import tempfile
from types import SimpleNamespace

import pytest

import pyrogram
from pyrogram import enums, types
from pyrogram.file_id import FileId, FileType

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
