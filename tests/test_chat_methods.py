import pytest

from pyrogram import enums, raw


class _Recorder:
    def __init__(self, result=True):
        self.calls = []
        self.result = result

    async def invoke(self, query, *args, **kwargs):
        self.calls.append(query)
        return self.result


async def test_reorder_folders_inserts_the_main_list_and_leaves_the_argument_alone():
    from pyrogram.methods.chats.reorder_folders import ReorderFolders

    class _Client(_Recorder, ReorderFolders):
        pass

    client = _Client()
    folder_ids = [2, 5, 4]

    await client.reorder_folders(folder_ids, main_chat_list_position=1)

    assert client.calls[0].order == [2, 0, 5, 4]
    assert folder_ids == [2, 5, 4]


async def test_reorder_folders_keeps_the_order_when_the_main_list_is_first():
    from pyrogram.methods.chats.reorder_folders import ReorderFolders

    class _Client(_Recorder, ReorderFolders):
        pass

    client = _Client()

    await client.reorder_folders([2, 5])

    assert client.calls[0].order == [2, 5]


async def test_toggle_folder_tags_passes_the_flag_through():
    from pyrogram.methods.chats.toggle_folder_tags import ToggleFolderTags

    class _Client(_Recorder, ToggleFolderTags):
        pass

    client = _Client()

    await client.toggle_folder_tags(False)

    assert client.calls[0].enabled is False


async def test_set_chat_member_tag_clears_the_tag_with_an_empty_rank():
    from pyrogram.methods.chats.set_chat_member_tag import SetChatMemberTag

    class _Client(_Recorder, SetChatMemberTag):
        async def resolve_peer(self, peer_id):
            return raw.types.InputPeerUser(user_id=1, access_hash=0)

    client = _Client()

    assert await client.set_chat_member_tag(-5, 1) is True
    assert client.calls[0].rank == ""


async def test_set_chat_discussion_group_needs_at_least_one_chat():
    from pyrogram.methods.chats.set_chat_discussion_group import SetChatDiscussionGroup

    class _Client(_Recorder, SetChatDiscussionGroup):
        async def resolve_peer(self, peer_id):
            raise AssertionError("must not resolve anything")

    with pytest.raises(ValueError):
        await _Client().set_chat_discussion_group()


async def test_set_chat_discussion_group_unlinks_with_an_empty_channel():
    from pyrogram.methods.chats.set_chat_discussion_group import SetChatDiscussionGroup

    class _Client(_Recorder, SetChatDiscussionGroup):
        async def resolve_peer(self, peer_id):
            return raw.types.InputPeerChannel(channel_id=7, access_hash=0)

    client = _Client()

    await client.set_chat_discussion_group(chat_id="@channel")

    assert isinstance(client.calls[0].broadcast, raw.types.InputPeerChannel)
    assert isinstance(client.calls[0].group, raw.types.InputChannelEmpty)


async def test_set_chat_discussion_group_rejects_a_user():
    from pyrogram.methods.chats.set_chat_discussion_group import SetChatDiscussionGroup

    class _Client(_Recorder, SetChatDiscussionGroup):
        async def resolve_peer(self, peer_id):
            return raw.types.InputPeerUser(user_id=1, access_hash=0)

    with pytest.raises(ValueError):
        await _Client().set_chat_discussion_group("@user", "@group")


async def test_set_chat_direct_messages_group_sends_the_star_price():
    from pyrogram.methods.chats.set_chat_direct_messages_group import SetChatDirectMessagesGroup

    class _Client(_Recorder, SetChatDirectMessagesGroup):
        async def resolve_peer(self, peer_id):
            return raw.types.InputPeerChannel(channel_id=7, access_hash=0)

    client = _Client()

    await client.set_chat_direct_messages_group(-100, 25, is_enabled=True)

    assert client.calls[0].send_paid_messages_stars == 25
    assert client.calls[0].broadcast_messages_allowed is True


async def test_set_main_profile_tab_splits_account_from_channel():
    from pyrogram.methods.chats.set_main_profile_tab import SetMainProfileTab

    class _Me(_Recorder, SetMainProfileTab):
        async def resolve_peer(self, peer_id):
            return raw.types.InputPeerSelf()

    class _Channel(_Recorder, SetMainProfileTab):
        async def resolve_peer(self, peer_id):
            return raw.types.InputPeerChannel(channel_id=7, access_hash=0)

    me = _Me()
    channel = _Channel()

    await me.set_main_profile_tab("me", enums.ProfileTab.GIFTS)
    await channel.set_main_profile_tab("@channel", enums.ProfileTab.GIFTS)

    assert isinstance(me.calls[0], raw.functions.account.SetMainProfileTab)
    assert isinstance(me.calls[0].tab, raw.types.ProfileTabGifts)
    assert isinstance(channel.calls[0], raw.functions.channels.SetMainProfileTab)


async def test_set_chat_accent_color_uses_the_account_request_for_yourself():
    from pyrogram.methods.chats.set_chat_accent_color import SetChatAccentColor

    class _Client(_Recorder, SetChatAccentColor):
        async def resolve_peer(self, peer_id):
            return raw.types.InputPeerSelf()

    client = _Client()

    await client.set_chat_accent_color("me", 5, for_profile=True)

    assert isinstance(client.calls[0], raw.functions.account.UpdateColor)
    assert client.calls[0].color.color == 5
    assert client.calls[0].for_profile is True


async def test_set_chat_accent_color_clears_the_color_when_nothing_is_given():
    from pyrogram.methods.chats.set_chat_accent_color import SetChatAccentColor

    class _Client(_Recorder, SetChatAccentColor):
        async def resolve_peer(self, peer_id):
            return raw.types.InputPeerSelf()

    client = _Client()

    await client.set_chat_accent_color("me")

    assert client.calls[0].color is None


async def test_set_chat_accent_color_uses_the_channel_request_for_a_channel():
    from pyrogram.methods.chats.set_chat_accent_color import SetChatAccentColor

    class _Client(_Recorder, SetChatAccentColor):
        async def resolve_peer(self, peer_id):
            return raw.types.InputPeerChannel(channel_id=7, access_hash=0)

    client = _Client(raw.types.Updates(updates=[], users=[], chats=[], date=0, seq=0))

    await client.set_chat_accent_color("@channel", 5)

    assert isinstance(client.calls[0], raw.functions.channels.UpdateColor)
    assert client.calls[0].color == 5


async def test_set_chat_accent_color_rejects_another_user():
    from pyrogram.methods.chats.set_chat_accent_color import SetChatAccentColor

    class _Client(_Recorder, SetChatAccentColor):
        async def resolve_peer(self, peer_id):
            return raw.types.InputPeerUser(user_id=1, access_hash=0)

    with pytest.raises(ValueError):
        await _Client().set_chat_accent_color("@user", 5)


async def test_transfer_chat_ownership_rejects_a_chat_that_is_not_a_channel():
    from pyrogram.methods.chats.transfer_chat_ownership import TransferChatOwnership

    class _Client(_Recorder, TransferChatOwnership):
        async def resolve_peer(self, peer_id):
            return raw.types.InputPeerChat(chat_id=5)

    with pytest.raises(ValueError):
        await _Client().transfer_chat_ownership(-5, 1, "password")


async def test_transfer_chat_ownership_accepts_your_own_account_as_the_new_owner():
    from pyrogram.methods.chats.transfer_chat_ownership import TransferChatOwnership

    class _Client(_Recorder, TransferChatOwnership):
        async def resolve_peer(self, peer_id):
            if peer_id == "me":
                return raw.types.InputPeerSelf()
            return raw.types.InputPeerChannel(channel_id=7, access_hash=0)

        async def invoke(self, query, *args, **kwargs):
            self.calls.append(query)

            if isinstance(query, raw.functions.account.GetPassword):
                raise RuntimeError("reached the password step")

            return True

    with pytest.raises(RuntimeError, match="reached the password step"):
        await _Client().transfer_chat_ownership(-100, "me", "password")


async def test_transfer_chat_ownership_rejects_a_new_owner_that_is_not_a_user():
    from pyrogram.methods.chats.transfer_chat_ownership import TransferChatOwnership

    class _Client(_Recorder, TransferChatOwnership):
        async def resolve_peer(self, peer_id):
            return raw.types.InputPeerChannel(channel_id=7, access_hash=0)

    with pytest.raises(ValueError):
        await _Client().transfer_chat_ownership(-100, "@channel", "password")


async def test_set_direct_messages_chat_topic_is_marked_as_unread():
    from pyrogram.methods.messages.set_direct_messages_chat_topic_is_marked_as_unread import (
        SetDirectMessagesChatTopicIsMarkedAsUnread,
    )

    class _Client(_Recorder, SetDirectMessagesChatTopicIsMarkedAsUnread):
        async def resolve_peer(self, peer_id):
            if peer_id == -100123456789:
                return raw.types.InputPeerChannel(channel_id=123456789, access_hash=0)
            return raw.types.InputPeerUser(user_id=peer_id, access_hash=0)

    client = _Client()
    res = await client.set_direct_messages_chat_topic_is_marked_as_unread(
        chat_id=-100123456789,
        topic_id=42,
        is_marked_as_unread=True,
    )

    assert res is True
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.messages.MarkDialogUnread)
    assert call.unread is True
    assert isinstance(call.parent_peer, raw.types.InputPeerChannel)
    assert call.parent_peer.channel_id == 123456789
    assert isinstance(call.peer, raw.types.InputDialogPeer)
    assert isinstance(call.peer.peer, raw.types.InputPeerUser)
    assert call.peer.peer.user_id == 42
