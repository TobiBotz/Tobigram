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


async def test_a_non_user_peer_in_a_basic_group_is_not_a_participant():
    from pyrogram.methods.chats.get_chat_member import GetChatMember

    class _Client(GetChatMember):
        async def resolve_peer(self, peer_id):
            if peer_id == "@group":
                return raw.types.InputPeerChat(chat_id=5)

            return raw.types.InputPeerChannel(channel_id=7, access_hash=0)

        async def invoke(self, query, *args, **kwargs):
            raise AssertionError("must not reach the server")

    with pytest.raises(UserNotParticipant):
        await _Client().get_chat_member("@group", "@somechannel")


async def test_basic_group_members_honour_the_limit():
    from pyrogram.methods.chats.get_chat_members import GetChatMembers

    participants = [raw.types.ChatParticipant(user_id=i, inviter_id=1, date=0) for i in (1, 2, 3)]

    class _Client(GetChatMembers):
        me = None

        async def resolve_peer(self, peer_id):
            return raw.types.InputPeerChat(chat_id=5)

        async def invoke(self, query, *args, **kwargs):
            return _chat_full(participants, [_user(i) for i in (1, 2, 3)])

    async def ids(**kwargs):
        return [m.user.id async for m in _Client().get_chat_members(5, **kwargs)]

    assert await ids(limit=2) == [1, 2]
    assert await ids() == [1, 2, 3]
    assert await ids(limit=0) == [1, 2, 3]


async def test_the_pinned_archive_folder_is_not_a_dialog():
    from pyrogram.methods.chats.get_dialogs_count import GetDialogsCount

    def dialog(uid):
        return raw.types.Dialog(
            peer=raw.types.PeerUser(user_id=uid),
            top_message=1,
            read_inbox_max_id=0,
            read_outbox_max_id=0,
            unread_count=0,
            unread_mentions_count=0,
            unread_reactions_count=0,
            unread_poll_votes_count=0,
            notify_settings=raw.types.PeerNotifySettings(),
        )

    folder = raw.types.DialogFolder(
        folder=raw.types.Folder(id=1, title="Archived"),
        peer=raw.types.PeerUser(user_id=1),
        top_message=1,
        unread_muted_peers_count=0,
        unread_unmuted_peers_count=0,
        unread_muted_messages_count=0,
        unread_unmuted_messages_count=0,
    )

    class _Client(GetDialogsCount):
        async def invoke(self, query, *args, **kwargs):
            return raw.types.messages.PeerDialogs(
                dialogs=[folder, dialog(1), dialog(2)],
                messages=[],
                chats=[],
                users=[],
                state=raw.types.updates.State(pts=0, qts=0, date=0, seq=0, unread_count=0),
            )

    assert await _Client().get_dialogs_count(pinned_only=True) == 2


async def test_unbanning_in_a_basic_group_does_not_ask_a_channel_rpc():
    """unban_chat_member always sent channels.EditBanned, which the server
    rejects with CHANNEL_INVALID for a basic group. Basic groups keep no ban
    list, so there is nothing to undo and the call succeeds without a request.
    """

    from pyrogram.methods.chats.unban_chat_member import UnbanChatMember

    sent = []

    class _Client(UnbanChatMember):
        async def resolve_peer(self, peer_id):
            return raw.types.InputPeerChat(chat_id=5) if peer_id == -5 else raw.types.InputPeerUser(user_id=1, access_hash=0)

        async def invoke(self, query, *args, **kwargs):
            sent.append(query)
            return raw.types.Updates(updates=[], users=[], chats=[], date=0, seq=0)

    assert await _Client().unban_chat_member(-5, 1) is True
    assert sent == []
