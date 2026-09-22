import inspect
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pyrogram
from pyrogram import enums
from pyrogram.types import Chat, Message


FORWARDED = {
    "animation": ("send_animation", ["file_name", "protect_content", "unsave"]),
    "audio": ("send_audio", ["file_name", "protect_content"]),
    "video": ("send_video", ["file_name", "protect_content", "view_once"]),
    "cached_media": (
        "send_cached_media",
        ["has_spoiler", "show_caption_above_media", "effect_id", "schedule_date", "protect_content"],
    ),
    "contact": ("send_contact", ["schedule_date", "protect_content", "suggested_post_parameters"]),
    "location": ("send_location", ["schedule_date", "protect_content", "suggested_post_parameters"]),
    "venue": ("send_venue", ["schedule_date", "protect_content", "suggested_post_parameters"]),
    "media_group": ("send_media_group", ["schedule_date", "protect_content", "show_caption_above_media"]),
    "sticker": ("send_sticker", ["protect_content", "emoji", "caption", "caption_entities"]),
    "voice": ("send_voice", ["protect_content", "waveform", "view_once"]),
    "photo": ("send_photo", ["view_once"]),
    "video_note": ("send_video_note", ["view_once"]),
    "live_photo": ("send_live_photo", ["has_spoiler", "schedule_date", "ephemeral_message_parameters"]),
    "game": ("send_game", ["protect_content"]),
    "inline_bot_result": ("send_inline_bot_result", ["schedule_date"]),
}

CASES = [
    (prefix + suffix, send, param)
    for suffix, (send, params) in FORWARDED.items()
    for prefix in ("reply_", "answer_")
    for param in params
]


class StubClient:
    def __init__(self):
        self.calls = {}

    def __getattr__(self, name):
        async def call(**kwargs):
            self.calls[name] = kwargs
            return "sent"

        return call


@pytest.fixture
def message():
    client = StubClient()

    return Message(
        id=42,
        chat=Chat(id=7, type=enums.ChatType.PRIVATE, client=client),
        client=client,
    )


@pytest.mark.parametrize("bound,send,param", CASES, ids=[f"{b}.{p}" for b, _, p in CASES])
def test_shortcut_exposes_the_param_its_send_method_has(bound, send, param):
    assert param in inspect.signature(getattr(pyrogram.Client, send)).parameters
    assert param in inspect.signature(getattr(Message, bound)).parameters
    assert f"{param}={param}," in inspect.getsource(getattr(Message, bound))


def test_callback_query_edit_message_text_forwards_link_preview_options():
    from pyrogram.types import CallbackQuery

    source = inspect.getsource(CallbackQuery.edit_message_text)

    assert "link_preview_options" in inspect.signature(CallbackQuery.edit_message_text).parameters
    assert source.count("link_preview_options=link_preview_options,") == 2


@pytest.mark.asyncio
async def test_reply_animation_forwards_the_new_params(message):
    await message.reply_animation("a.gif", file_name="x.gif", protect_content=True, unsave=True)

    sent = message._client.calls["send_animation"]

    assert sent["file_name"] == "x.gif"
    assert sent["protect_content"] is True
    assert sent["unsave"] is True


@pytest.mark.asyncio
async def test_reply_rich_replies_to_the_bound_message(message):
    await message.reply_rich("# hi", protect_content=True)

    sent = message._client.calls["send_rich_message"]

    assert sent["chat_id"] == 7
    assert sent["rich_text"] == "# hi"
    assert sent["protect_content"] is True
    assert sent["reply_parameters"].message_id == 42


@pytest.mark.asyncio
async def test_answer_rich_does_not_reply(message):
    await message.answer_rich("# hi")

    assert message._client.calls["send_rich_message"]["reply_parameters"] is None
