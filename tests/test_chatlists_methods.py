import pytest

import pyrogram
from pyrogram import raw


class _Recorder:
    def __init__(self, result=True):
        self.calls = []
        self.result = result

    async def invoke(self, query, *args, **kwargs):
        self.calls.append(query)
        return self.result

    async def resolve_peer(self, peer_id):
        if peer_id == "me":
            return raw.types.InputPeerSelf()
        uid = int(peer_id) if isinstance(peer_id, int) else 12345
        return raw.types.InputPeerChannel(channel_id=uid, access_hash=0)


@pytest.mark.asyncio
async def test_get_chatlist_updates_dispatches_query():
    from pyrogram.methods.folders.get_chatlist_updates import GetChatlistUpdates

    class _Client(_Recorder, GetChatlistUpdates):
        pass

    dummy_updates = raw.types.chatlists.ChatlistUpdates(missing_peers=[], chats=[], users=[])
    client = _Client(result=dummy_updates)

    # With integer folder ID
    res = await client.get_chatlist_updates(2)
    assert res == dummy_updates
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.chatlists.GetChatlistUpdates)
    assert isinstance(call.chatlist, raw.types.InputChatlistDialogFilter)
    assert call.chatlist.filter_id == 2

    # With InputChatlist object
    chatlist_obj = raw.types.InputChatlistDialogFilter(filter_id=5)
    res2 = await client.get_chatlist_updates(chatlist_obj)
    assert res2 == dummy_updates
    assert len(client.calls) == 2
    assert client.calls[1].chatlist == chatlist_obj


@pytest.mark.asyncio
async def test_get_leave_chatlist_suggestions_dispatches_query():
    from pyrogram.methods.folders.get_leave_chatlist_suggestions import GetLeaveChatlistSuggestions

    class _Client(_Recorder, GetLeaveChatlistSuggestions):
        pass

    dummy_peers = [raw.types.PeerChannel(channel_id=123)]
    client = _Client(result=dummy_peers)

    res = await client.get_leave_chatlist_suggestions(2)
    assert res == dummy_peers
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.chatlists.GetLeaveChatlistSuggestions)
    assert isinstance(call.chatlist, raw.types.InputChatlistDialogFilter)
    assert call.chatlist.filter_id == 2


@pytest.mark.asyncio
async def test_hide_chatlist_updates_dispatches_query():
    from pyrogram.methods.folders.hide_chatlist_updates import HideChatlistUpdates

    class _Client(_Recorder, HideChatlistUpdates):
        pass

    client = _Client(result=True)
    res = await client.hide_chatlist_updates(2)

    assert res is True
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.chatlists.HideChatlistUpdates)
    assert isinstance(call.chatlist, raw.types.InputChatlistDialogFilter)
    assert call.chatlist.filter_id == 2


@pytest.mark.asyncio
async def test_join_chatlist_updates_dispatches_query():
    from pyrogram.methods.folders.join_chatlist_updates import JoinChatlistUpdates

    class _Client(_Recorder, JoinChatlistUpdates):
        pass

    dummy_updates = raw.types.Updates(updates=[], users=[], chats=[], date=0, seq=0)
    client = _Client(result=dummy_updates)

    res = await client.join_chatlist_updates(2, peers=["my_channel", 98765])

    assert res == dummy_updates
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.chatlists.JoinChatlistUpdates)
    assert isinstance(call.chatlist, raw.types.InputChatlistDialogFilter)
    assert call.chatlist.filter_id == 2
    assert len(call.peers) == 2
    assert isinstance(call.peers[0], raw.types.InputPeerChannel)
    assert isinstance(call.peers[1], raw.types.InputPeerChannel)


def test_client_has_all_new_chatlists_methods():
    client_methods = dir(pyrogram.Client)
    expected_methods = [
        "get_chatlist_updates",
        "get_leave_chatlist_suggestions",
        "hide_chatlist_updates",
        "join_chatlist_updates",
    ]
    for method in expected_methods:
        assert method in client_methods, f"Client is missing method: {method}"
