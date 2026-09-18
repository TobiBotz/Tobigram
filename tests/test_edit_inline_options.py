import pytest

import pyrogram
from pyrogram import enums, raw, types, utils
from pyrogram.parser import Parser


class FakeStorage:
    async def dc_id(self):
        return 2


class FakeClient:
    sleep_threshold = 10
    link_preview_options = None
    parse_mode = enums.ParseMode.DEFAULT

    def __init__(self):
        self.storage = FakeStorage()
        self.parser = Parser(self)
        self.sent = None

    async def invoke(self, query, sleep_threshold=None, business_connection_id=None):
        self.sent = query
        return True

    edit_inline_text = pyrogram.Client.edit_inline_text
    edit_inline_caption = pyrogram.Client.edit_inline_caption


@pytest.fixture
def inline_message_id():
    return utils.pack_inline_message_id(
        raw.types.InputBotInlineMessageID(dc_id=2, id=1, access_hash=1)
    )


@pytest.fixture
def client():
    return FakeClient()


async def test_entities_reach_the_request(client, inline_message_id):
    entities = [
        types.MessageEntity(type=enums.MessageEntityType.BOLD, offset=0, length=6),
        types.MessageEntity(type=enums.MessageEntityType.SPOILER, offset=7, length=6),
    ]

    await client.edit_inline_text(inline_message_id, "entity hidden", entities=entities)

    assert client.sent.message == "entity hidden"
    assert [type(e).__name__ for e in client.sent.entities] == [
        "MessageEntityBold",
        "MessageEntitySpoiler",
    ]


async def test_a_disabled_preview_sets_no_webpage(client, inline_message_id):
    await client.edit_inline_text(
        inline_message_id,
        "see https://docs.tobigram.com",
        entities=[],
        link_preview_options=types.LinkPreviewOptions(is_disabled=True),
    )

    assert client.sent.no_webpage is True
    assert client.sent.media is None


async def test_a_preview_url_becomes_a_web_page_media(client, inline_message_id):
    await client.edit_inline_text(
        inline_message_id,
        "text",
        entities=[],
        link_preview_options=types.LinkPreviewOptions(
            url="https://docs.tobigram.com", show_above_text=True, prefer_large_media=True
        ),
    )

    assert isinstance(client.sent.media, raw.types.InputMediaWebPage)
    assert client.sent.media.url == "https://docs.tobigram.com"
    assert client.sent.media.force_large_media is True
    assert client.sent.invert_media is True


async def test_disable_web_page_preview_still_wins(client, inline_message_id):
    await client.edit_inline_text(
        inline_message_id, "text", entities=[], disable_web_page_preview=True
    )

    assert client.sent.no_webpage is True


async def test_caption_entities_and_position_reach_the_request(client, inline_message_id):
    await client.edit_inline_caption(
        inline_message_id,
        "listed entities",
        caption_entities=[
            types.MessageEntity(type=enums.MessageEntityType.ITALIC, offset=0, length=6)
        ],
        show_caption_above_media=True,
    )

    assert client.sent.message == "listed entities"
    assert [type(e).__name__ for e in client.sent.entities] == ["MessageEntityItalic"]
    assert client.sent.invert_media is True


async def test_a_string_copy_text_becomes_a_button():
    button = types.InlineKeyboardButton("copy", copy_text="plain string")

    assert isinstance(button.copy_text, types.CopyTextButton)
    assert button.copy_text.text == "plain string"

    written = await button.write(None)

    assert written.type.copy_text == "plain string"


async def test_a_copy_text_button_is_left_alone():
    button = types.InlineKeyboardButton("copy", copy_text=types.CopyTextButton("kept"))

    assert button.copy_text.text == "kept"
