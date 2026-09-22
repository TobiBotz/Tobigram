import pytest

import pyrogram
from pyrogram import raw, types


class _Recorder:
    def __init__(self, result=True):
        self.calls = []
        self.result = result

    async def invoke(self, query, *args, **kwargs):
        self.calls.append(query)
        return self.result

    async def resolve_peer(self, peer_id):
        if peer_id == "me" or peer_id == 111:
            return raw.types.InputPeerSelf()
        return raw.types.InputPeerChannel(
            channel_id=int(peer_id) if isinstance(peer_id, int) else 999,
            access_hash=123,
        )


@pytest.mark.asyncio
async def test_create_community_dispatches_query():
    from pyrogram.methods.communities.create_community import CreateCommunity

    class _Client(_Recorder, CreateCommunity):
        pass

    client = _Client(result=raw.types.Updates(updates=[], users=[], chats=[], date=0, seq=0))
    res = await client.create_community("Developers", 123, about="About dev", hidden=True)

    assert isinstance(res, raw.types.Updates)
    call = client.calls[0]
    assert isinstance(call, raw.functions.communities.Create)
    assert call.title == "Developers"
    assert call.about == "About dev"
    assert call.hidden is True
    assert call.peer.channel_id == 123


@pytest.mark.asyncio
async def test_get_joined_communities_parses_chats():
    from pyrogram.methods.communities.get_joined_communities import GetJoinedCommunities

    raw_chat = raw.types.Channel(
        id=555,
        title="Community Root",
        photo=raw.types.ChatPhotoEmpty(),
        date=1700000000,
    )

    class _Client(_Recorder, GetJoinedCommunities):
        pass

    client = _Client(result=raw.types.messages.Chats(chats=[raw_chat]))
    chats = await client.get_joined_communities()

    assert len(chats) == 1
    assert isinstance(chats[0], types.Chat)
    assert chats[0].id == -1000000000555
    assert isinstance(client.calls[0], raw.functions.communities.GetJoinedCommunities)


@pytest.mark.asyncio
async def test_get_participant_joined_community_chats_dispatches_query():
    from pyrogram.methods.communities.get_participant_joined_community_chats import (
        GetParticipantJoinedCommunityChats,
    )

    class _Client(_Recorder, GetParticipantJoinedCommunityChats):
        pass

    client = _Client()
    await client.get_participant_joined_community_chats(123, 456)
    call = client.calls[0]
    assert isinstance(call, raw.functions.communities.GetParticipantJoinedChats)
    assert call.community.channel_id == 123
    assert call.participant.channel_id == 456


@pytest.mark.asyncio
async def test_get_community_link_requests_dispatches_query():
    from pyrogram.methods.communities.get_community_link_requests import GetCommunityLinkRequests

    class _Client(_Recorder, GetCommunityLinkRequests):
        pass

    client = _Client()
    await client.get_community_link_requests(123, offset="abc", limit=50)
    call = client.calls[0]
    assert isinstance(call, raw.functions.communities.GetPeerLinkRequests)
    assert call.community.channel_id == 123
    assert call.offset == "abc"
    assert call.limit == 50


@pytest.mark.asyncio
async def test_toggle_all_community_link_requests_dispatches_query():
    from pyrogram.methods.communities.toggle_all_community_link_requests import (
        ToggleAllCommunityLinkRequests,
    )

    class _Client(_Recorder, ToggleAllCommunityLinkRequests):
        pass

    client = _Client()
    await client.toggle_all_community_link_requests(123, reject=True)
    call = client.calls[0]
    assert isinstance(call, raw.functions.communities.ToggleAllPeerLinkRequestApproval)
    assert call.community.channel_id == 123
    assert call.reject is True


@pytest.mark.asyncio
async def test_collapse_community_dispatches_query():
    from pyrogram.methods.communities.collapse_community import CollapseCommunity

    class _Client(_Recorder, CollapseCommunity):
        pass

    client = _Client()
    await client.collapse_community(123, collapsed=True)
    call = client.calls[0]
    assert isinstance(call, raw.functions.communities.ToggleCommunityCollapsedInDialogs)
    assert call.community.channel_id == 123
    assert call.collapsed is True


@pytest.mark.asyncio
async def test_ban_community_participant_dispatches_query():
    from pyrogram.methods.communities.ban_community_participant import BanCommunityParticipant

    class _Client(_Recorder, BanCommunityParticipant):
        pass

    client = _Client()
    await client.ban_community_participant(123, 456, unban=False)
    call = client.calls[0]
    assert isinstance(call, raw.functions.communities.ToggleParticipantBanned)
    assert call.community.channel_id == 123
    assert call.participant.channel_id == 456
    assert call.unban is False


@pytest.mark.asyncio
async def test_toggle_community_chat_link_dispatches_query():
    from pyrogram.methods.communities.toggle_community_chat_link import ToggleCommunityChatLink

    class _Client(_Recorder, ToggleCommunityChatLink):
        pass

    client = _Client()
    await client.toggle_community_chat_link(123, 789, visible=True)
    call = client.calls[0]
    assert isinstance(call, raw.functions.communities.TogglePeerLink)
    assert call.community.channel_id == 123
    assert call.peer.channel_id == 789
    assert call.visible is True


@pytest.mark.asyncio
async def test_approve_community_link_request_dispatches_query():
    from pyrogram.methods.communities.approve_community_link_request import (
        ApproveCommunityLinkRequest,
    )

    class _Client(_Recorder, ApproveCommunityLinkRequest):
        pass

    client = _Client()
    await client.approve_community_link_request(123, 789, reject=None)
    call = client.calls[0]
    assert isinstance(call, raw.functions.communities.TogglePeerLinkRequestApproval)
    assert call.community.channel_id == 123
    assert call.peer.channel_id == 789
    assert call.reject is None
