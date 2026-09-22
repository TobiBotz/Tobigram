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
        return raw.types.InputPeerUser(user_id=uid, access_hash=0)


@pytest.mark.asyncio
async def test_accept_contact_dispatches_query():
    from pyrogram.methods.contacts.accept_contact import AcceptContact

    class _Client(_Recorder, AcceptContact):
        pass

    dummy_updates = raw.types.Updates(updates=[], users=[], chats=[], date=0, seq=0)
    client = _Client(result=dummy_updates)
    res = await client.accept_contact(12345)

    assert res == dummy_updates
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.contacts.AcceptContact)
    assert isinstance(call.id, raw.types.InputPeerUser)
    assert call.id.user_id == 12345


@pytest.mark.asyncio
async def test_block_from_replies_dispatches_query():
    from pyrogram.methods.contacts.block_from_replies import BlockFromReplies

    class _Client(_Recorder, BlockFromReplies):
        pass

    dummy_updates = raw.types.Updates(updates=[], users=[], chats=[], date=0, seq=0)
    client = _Client(result=dummy_updates)
    res = await client.block_from_replies(
        msg_id=999,
        delete_message=True,
        delete_history=False,
        report_spam=True,
    )

    assert res == dummy_updates
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.contacts.BlockFromReplies)
    assert call.msg_id == 999
    assert call.delete_message is True
    assert call.delete_history is False
    assert call.report_spam is True


@pytest.mark.asyncio
async def test_delete_contacts_by_phones_dispatches_query():
    from pyrogram.methods.contacts.delete_contacts_by_phones import DeleteContactsByPhones

    class _Client(_Recorder, DeleteContactsByPhones):
        pass

    client = _Client(result=True)
    res = await client.delete_contacts_by_phones(["+1234567890", "+9876543210"])

    assert res is True
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.contacts.DeleteByPhones)
    assert call.phones == ["+1234567890", "+9876543210"]


@pytest.mark.asyncio
async def test_edit_close_friends_dispatches_query():
    from pyrogram.methods.contacts.edit_close_friends import EditCloseFriends

    class _Client(_Recorder, EditCloseFriends):
        pass

    client = _Client(result=True)
    res = await client.edit_close_friends([111, 222])

    assert res is True
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.contacts.EditCloseFriends)
    assert call.id == [111, 222]


@pytest.mark.asyncio
async def test_export_contact_token_dispatches_query():
    from pyrogram.methods.contacts.export_contact_token import ExportContactToken

    class _Client(_Recorder, ExportContactToken):
        pass

    dummy_token = raw.types.ExportedContactToken(url="tg://contact?token=abc", expires=1700000000)
    client = _Client(result=dummy_token)
    res = await client.export_contact_token()

    assert res == dummy_token
    assert len(client.calls) == 1
    assert isinstance(client.calls[0], raw.functions.contacts.ExportContactToken)


@pytest.mark.asyncio
async def test_get_contact_ids_dispatches_query():
    from pyrogram.methods.contacts.get_contact_ids import GetContactIDs

    class _Client(_Recorder, GetContactIDs):
        pass

    client = _Client(result=[111, 222, 333])
    res = await client.get_contact_ids(hash=42)

    assert res == [111, 222, 333]
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.contacts.GetContactIDs)
    assert call.hash == 42


@pytest.mark.asyncio
async def test_get_sponsored_peers_dispatches_query():
    from pyrogram.methods.contacts.get_sponsored_peers import GetSponsoredPeers

    class _Client(_Recorder, GetSponsoredPeers):
        pass

    dummy_peers = raw.types.contacts.SponsoredPeers(peers=[], chats=[], users=[])
    client = _Client(result=dummy_peers)
    res = await client.get_sponsored_peers("crypto")

    assert res == dummy_peers
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.contacts.GetSponsoredPeers)
    assert call.q == "crypto"


@pytest.mark.asyncio
async def test_get_contact_statuses_dispatches_query():
    from pyrogram.methods.contacts.get_contact_statuses import GetContactStatuses

    class _Client(_Recorder, GetContactStatuses):
        pass

    dummy_statuses = [
        raw.types.ContactStatus(
            user_id=123,
            status=raw.types.UserStatusOnline(expires=1700000000),
        )
    ]
    client = _Client(result=dummy_statuses)
    res = await client.get_contact_statuses()

    assert res == dummy_statuses
    assert len(client.calls) == 1
    assert isinstance(client.calls[0], raw.functions.contacts.GetStatuses)


@pytest.mark.asyncio
async def test_import_contact_token_dispatches_query():
    from pyrogram.methods.contacts.import_contact_token import ImportContactToken

    class _Client(_Recorder, ImportContactToken):
        pass

    dummy_user = raw.types.User(id=123)
    client = _Client(result=dummy_user)
    res = await client.import_contact_token("token_abc")

    assert res == dummy_user
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.contacts.ImportContactToken)
    assert call.token == "token_abc"


@pytest.mark.asyncio
async def test_reset_saved_contacts_dispatches_query():
    from pyrogram.methods.contacts.reset_saved_contacts import ResetSavedContacts

    class _Client(_Recorder, ResetSavedContacts):
        pass

    client = _Client(result=True)
    res = await client.reset_saved_contacts()

    assert res is True
    assert len(client.calls) == 1
    assert isinstance(client.calls[0], raw.functions.contacts.ResetSaved)


@pytest.mark.asyncio
async def test_reset_top_peer_rating_dispatches_query():
    from pyrogram.methods.contacts.reset_top_peer_rating import ResetTopPeerRating

    class _Client(_Recorder, ResetTopPeerRating):
        pass

    category = raw.types.TopPeerCategoryCorrespondents()
    client = _Client(result=True)
    res = await client.reset_top_peer_rating(category, 12345)

    assert res is True
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.contacts.ResetTopPeerRating)
    assert call.category == category
    assert isinstance(call.peer, raw.types.InputPeerUser)
    assert call.peer.user_id == 12345


@pytest.mark.asyncio
async def test_resolve_phone_dispatches_query():
    from pyrogram.methods.contacts.resolve_phone import ResolvePhone

    class _Client(_Recorder, ResolvePhone):
        pass

    dummy_resolved = raw.types.contacts.ResolvedPeer(
        peer=raw.types.PeerUser(user_id=123),
        chats=[],
        users=[],
    )

    client = _Client(result=dummy_resolved)
    res = await client.resolve_phone("+1234567890")

    assert res == dummy_resolved
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.contacts.ResolvePhone)
    assert call.phone == "+1234567890"


@pytest.mark.asyncio
async def test_set_blocked_dispatches_query():
    from pyrogram.methods.contacts.set_blocked import SetBlocked

    class _Client(_Recorder, SetBlocked):
        pass

    client = _Client(result=True)
    res = await client.set_blocked([111, 222], my_stories_from=True, limit=50)

    assert res is True
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.contacts.SetBlocked)
    assert len(call.id) == 2
    assert isinstance(call.id[0], raw.types.InputPeerUser)
    assert call.id[0].user_id == 111
    assert isinstance(call.id[1], raw.types.InputPeerUser)
    assert call.id[1].user_id == 222
    assert call.my_stories_from is True
    assert call.limit == 50


@pytest.mark.asyncio
async def test_toggle_top_peers_dispatches_query():
    from pyrogram.methods.contacts.toggle_top_peers import ToggleTopPeers

    class _Client(_Recorder, ToggleTopPeers):
        pass

    client = _Client(result=True)
    res = await client.toggle_top_peers(False)

    assert res is True
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.contacts.ToggleTopPeers)
    assert call.enabled is False


def test_client_has_all_new_contacts_methods():
    client_methods = dir(pyrogram.Client)
    expected_methods = [
        "accept_contact",
        "block_from_replies",
        "delete_contacts_by_phones",
        "edit_close_friends",
        "export_contact_token",
        "get_contact_ids",
        "get_sponsored_peers",
        "get_contact_statuses",
        "import_contact_token",
        "reset_saved_contacts",
        "reset_top_peer_rating",
        "resolve_phone",
        "set_blocked",
        "toggle_top_peers",
    ]
    for method in expected_methods:
        assert method in client_methods, f"Client is missing method: {method}"
