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


async def test_pinning_in_a_private_chat_is_documented_to_return_none():
    from pyrogram.methods.chats.pin_chat_message import PinChatMessage

    class _Client(PinChatMessage):
        async def resolve_peer(self, peer_id):
            return raw.types.InputPeerSelf()

        async def invoke(self, query, *args, **kwargs):
            return raw.types.Updates(updates=[], users=[], chats=[], date=0, seq=0)

    assert await _Client().pin_chat_message("me", 1) is None
    assert "None" in PinChatMessage.pin_chat_message.__doc__
