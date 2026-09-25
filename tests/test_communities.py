import pytest
from pyrogram import Client, raw, types


class FakeCommunitiesClient(Client):
    def __init__(self):
        super().__init__("test_session", api_id=12345, api_hash="0123456789abcdef0123456789abcdef")
        self.invoked = []
        self._invoke_return = True

    def set_return(self, val):
        self._invoke_return = val

    async def invoke(self, query):
        self.invoked.append(query)
        return self._invoke_return

    async def resolve_peer(self, peer_id):
        if isinstance(peer_id, int) or str(peer_id).isdigit():
            return raw.types.InputPeerChannel(channel_id=int(peer_id), access_hash=789)
        return raw.types.InputPeerSelf()


@pytest.fixture
def client():
    return FakeCommunitiesClient()


class DummyUpdates:
    pass


class DummyPeerLinkRequests:
    pass


class DummyParticipantJoinedChats:
    pass


@pytest.mark.asyncio
async def test_approve_community_link_request(client):
    client.set_return(True)
    res = await client.approve_community_link_request(1001, 2002)
    assert res is True
    assert len(client.invoked) == 1
    req = client.invoked[-1]
    assert isinstance(req, raw.functions.communities.TogglePeerLinkRequestApproval)
    assert isinstance(req.community, raw.types.InputChannel)
    assert req.community.channel_id == 1001


@pytest.mark.asyncio
async def test_ban_community_participant(client):
    client.set_return(True)
    res = await client.ban_community_participant(1001, 555)
    assert res is True
    req = client.invoked[-1]
    assert isinstance(req, raw.functions.communities.ToggleParticipantBanned)
    assert isinstance(req.community, raw.types.InputChannel)


@pytest.mark.asyncio
async def test_collapse_community(client):
    client.set_return(DummyUpdates())
    await client.collapse_community(1001, True)
    req = client.invoked[-1]
    assert isinstance(req, raw.functions.communities.ToggleCommunityCollapsedInDialogs)
    assert isinstance(req.community, raw.types.InputChannel)
    assert req.collapsed is True


@pytest.mark.asyncio
async def test_create_community(client):
    client.set_return(DummyUpdates())
    await client.create_community(title="Test Community", chat_id=1001)
    req = client.invoked[-1]
    assert isinstance(req, raw.functions.communities.Create)
    assert req.title == "Test Community"


@pytest.mark.asyncio
async def test_get_community_link_requests(client):
    client.set_return(DummyPeerLinkRequests())
    await client.get_community_link_requests(1001)
    req = client.invoked[-1]
    assert isinstance(req, raw.functions.communities.GetPeerLinkRequests)
    assert isinstance(req.community, raw.types.InputChannel)


@pytest.mark.asyncio
async def test_get_participant_joined_community_chats(client):
    client.set_return(DummyParticipantJoinedChats())
    await client.get_participant_joined_community_chats(1001, "me")
    req = client.invoked[-1]
    assert isinstance(req, raw.functions.communities.GetParticipantJoinedChats)
    assert isinstance(req.community, raw.types.InputChannel)


@pytest.mark.asyncio
async def test_toggle_all_community_link_requests(client):
    client.set_return(True)
    await client.toggle_all_community_link_requests(1001, reject=True)
    req = client.invoked[-1]
    assert isinstance(req, raw.functions.communities.ToggleAllPeerLinkRequestApproval)
    assert isinstance(req.community, raw.types.InputChannel)
    assert req.reject is True


@pytest.mark.asyncio
async def test_toggle_community_chat_link(client):
    client.set_return(True)
    await client.toggle_community_chat_link(1001, 2002, visible=True)
    req = client.invoked[-1]
    assert isinstance(req, raw.functions.communities.TogglePeerLink)
    assert isinstance(req.community, raw.types.InputChannel)
    assert isinstance(req.peer, raw.types.InputPeerChannel)
    assert req.visible is True


def test_community_chat_added_parse():
    client = FakeCommunitiesClient()
    action = raw.types.MessageActionChangeCommunity(community_id=1001)
    raw_comm = raw.types.Community(
        id=1001,
        access_hash=123,
        title="My Community",
        photo=raw.types.ChatPhotoEmpty(),
        date=1700000000,
        creator=True,
    )
    chats = {1001: raw_comm}
    parsed = types.CommunityChatAdded._parse(client, action, chats)
    assert parsed is not None
    assert parsed.community_id == 1001
    assert parsed.community is not None
    assert parsed.community.title == "My Community"
