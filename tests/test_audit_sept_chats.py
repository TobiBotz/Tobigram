import pytest

from pyrogram import raw, types
from pyrogram.errors import UserNotParticipant


def _channel(**kwargs):
    kwargs.setdefault("usernames", [])
    kwargs.setdefault("restriction_reason", [])

    return raw.types.Channel(id=7, title="t", photo=raw.types.ChatPhotoEmpty(), date=0, **kwargs)


def _user(uid):
    return raw.types.User(id=uid, first_name=f"u{uid}", usernames=[], restriction_reason=[])


def _chat_full(participants, users):
    return raw.types.messages.ChatFull(
        full_chat=raw.types.ChatFull(
            id=5,
            about="",
            participants=raw.types.ChatParticipants(chat_id=5, participants=participants, version=1),
            notify_settings=raw.types.PeerNotifySettings(),
        ),
        chats=[],
        users=users,
    )


async def test_an_expired_custom_emoji_id_is_skipped_not_crashed():
    from pyrogram.methods.messages.get_custom_emoji_stickers import GetCustomEmojiStickers

    class _Client(GetCustomEmojiStickers):
        async def invoke(self, query, *args, **kwargs):
            return [raw.types.DocumentEmpty(id=1)]

    assert await _Client().get_custom_emoji_stickers([1]) == []
