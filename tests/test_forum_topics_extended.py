from __future__ import annotations

from unittest.mock import AsyncMock, patch
import pytest

import pyrogram
from pyrogram import raw, types


@pytest.fixture
def client():
    app = pyrogram.Client("test", api_id=12345, api_hash="0123456789abcdef0123456789abcdef")
    app.resolve_peer = AsyncMock(
        return_value=raw.types.InputPeerChannel(channel_id=100, access_hash=200)
    )
    app.invoke = AsyncMock(return_value=True)
    return app


@pytest.mark.asyncio
async def test_reopen_forum_topic(client):
    res = await client.reopen_forum_topic("chat_username", 42)
    assert res is True
    client.invoke.assert_called_once()
    call_arg = client.invoke.call_args[0][0]
    assert isinstance(call_arg, raw.functions.messages.EditForumTopic)
    assert call_arg.topic_id == 42
    assert call_arg.closed is False


@pytest.mark.asyncio
async def test_close_general_forum_topic(client):
    res = await client.close_general_forum_topic("chat_username")
    assert res is True
    client.invoke.assert_called_once()
    call_arg = client.invoke.call_args[0][0]
    assert isinstance(call_arg, raw.functions.messages.EditForumTopic)
    assert call_arg.topic_id == 1
    assert call_arg.closed is True


@pytest.mark.asyncio
async def test_reopen_general_forum_topic(client):
    res = await client.reopen_general_forum_topic("chat_username")
    assert res is True
    client.invoke.assert_called_once()
    call_arg = client.invoke.call_args[0][0]
    assert isinstance(call_arg, raw.functions.messages.EditForumTopic)
    assert call_arg.topic_id == 1
    assert call_arg.closed is False


@pytest.mark.asyncio
async def test_edit_general_forum_topic(client):
    res = await client.edit_general_forum_topic("chat_username", "New Title")
    assert res is True
    client.invoke.assert_called_once()
    call_arg = client.invoke.call_args[0][0]
    assert isinstance(call_arg, raw.functions.messages.EditForumTopic)
    assert call_arg.topic_id == 1
    assert call_arg.title == "New Title"


@pytest.mark.asyncio
async def test_hide_general_forum_topic(client):
    res = await client.hide_general_forum_topic("chat_username")
    assert res is True
    client.invoke.assert_called_once()
    call_arg = client.invoke.call_args[0][0]
    assert isinstance(call_arg, raw.functions.messages.EditForumTopic)
    assert call_arg.topic_id == 1
    assert call_arg.hidden is True


@pytest.mark.asyncio
async def test_unhide_general_forum_topic(client):
    res = await client.unhide_general_forum_topic("chat_username")
    assert res is True
    client.invoke.assert_called_once()
    call_arg = client.invoke.call_args[0][0]
    assert isinstance(call_arg, raw.functions.messages.EditForumTopic)
    assert call_arg.topic_id == 1
    assert call_arg.hidden is False


@pytest.mark.asyncio
async def test_unpin_all_forum_topic_messages(client):
    client.unpin_all_chat_messages = AsyncMock(return_value=True)
    res = await client.unpin_all_forum_topic_messages("chat_username", 55)
    assert res is True
    client.unpin_all_chat_messages.assert_called_once_with(chat_id="chat_username", top_msg_id=55)


@pytest.mark.asyncio
async def test_unpin_all_general_forum_topic_messages(client):
    client.unpin_all_chat_messages = AsyncMock(return_value=True)
    res = await client.unpin_all_general_forum_topic_messages("chat_username")
    assert res is True
    client.unpin_all_chat_messages.assert_called_once_with(chat_id="chat_username", top_msg_id=1)


@pytest.mark.asyncio
async def test_get_forum_topic_icon_stickers(client):
    fake_sticker_set = types.StickerSet(
        id=1,
        name="icons",
        title="Icons",
        sticker_type=pyrogram.enums.StickerType.CUSTOM_EMOJI,
        stickers=[
            types.Sticker(
                file_id="abc",
                file_unique_id="xyz",
                type=pyrogram.enums.StickerType.CUSTOM_EMOJI,
                width=512,
                height=512,
                is_animated=False,
                is_video=False,
            )
        ],
    )
    with patch.object(types.StickerSet, "_parse", new=AsyncMock(return_value=fake_sticker_set)):
        stickers = await client.get_forum_topic_icon_stickers()
        assert len(stickers) == 1
        assert stickers[0].file_id == "abc"
        client.invoke.assert_called_once()
        call_arg = client.invoke.call_args[0][0]
        assert isinstance(call_arg, raw.functions.messages.GetStickerSet)
        assert isinstance(call_arg.stickerset, raw.types.InputStickerSetEmojiDefaultTopicIcons)
