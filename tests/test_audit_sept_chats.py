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


async def test_translating_without_a_target_language_is_a_clear_error():
    from pyrogram.methods.messages.translate_text import TranslateText

    class _Client(TranslateText):
        async def invoke(self, query, *args, **kwargs):
            raise AssertionError("must not reach the server")

    with pytest.raises(ValueError):
        await _Client().translate_text(text="hi")


def test_join_by_request_is_parsed_for_a_channel():
    assert types.Chat._parse_channel_chat(None, _channel(join_request=True)).join_by_request is True
    assert types.Chat._parse_channel_chat(None, _channel()).join_by_request is None


async def test_migrated_from_max_message_id_is_populated():
    from pyrogram.types.user_and_chats.chat import Chat

    class _Client:
        me = None

        async def get_messages(self, *args, **kwargs):
            return None

        async def invoke(self, query, *args, **kwargs):
            return raw.types.messages.ChatFull(
                full_chat=raw.types.ChannelFull(
                    id=7,
                    about="",
                    read_inbox_max_id=0,
                    read_outbox_max_id=0,
                    unread_count=0,
                    chat_photo=raw.types.PhotoEmpty(id=0),
                    notify_settings=raw.types.PeerNotifySettings(),
                    bot_info=[],
                    pts=0,
                    migrated_from_chat_id=5,
                    migrated_from_max_id=42,
                ),
                chats=[_channel(megagroup=True)],
                users=[],
            )

    chat = await Chat._parse_full(_Client(), await _Client().invoke(None))

    assert chat.migrated_from_max_message_id == 42
    assert not hasattr(chat, "migrated_from_max_id")


async def test_banning_from_a_basic_group_by_username_uses_the_resolved_id():
    from pyrogram.methods.chats.ban_chat_member import BanChatMember

    class _Client(BanChatMember):
        sent = None

        async def resolve_peer(self, peer_id):
            if peer_id == "@group":
                return raw.types.InputPeerChat(chat_id=5)

            return raw.types.InputPeerUser(user_id=9, access_hash=0)

        async def invoke(self, query, *args, **kwargs):
            self.sent = query

            return raw.types.Updates(updates=[], users=[], chats=[], date=0, seq=0)

    client = _Client()

    assert await client.ban_chat_member("@group", 9) is True
    assert client.sent.chat_id == 5
