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
async def test_get_boosts_list_dispatches_query():
    from pyrogram.methods.premium.get_boosts_list import GetBoostsList

    class _Client(_Recorder, GetBoostsList):
        pass

    dummy_list = raw.types.premium.BoostsList(
        count=1,
        boosts=[],
        users=[],
        next_offset="next_page",
    )
    client = _Client(result=dummy_list)
    res = await client.get_boosts_list(
        chat_id=12345,
        offset="off_1",
        limit=20,
        gifts=True,
    )

    assert res == dummy_list
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.premium.GetBoostsList)
    assert isinstance(call.peer, raw.types.InputPeerUser)
    assert call.peer.user_id == 12345
    assert call.offset == "off_1"
    assert call.limit == 20
    assert call.gifts is True


@pytest.mark.asyncio
async def test_get_user_boosts_dispatches_query():
    from pyrogram.methods.premium.get_user_boosts import GetUserBoosts

    class _Client(_Recorder, GetUserBoosts):
        pass

    dummy_list = raw.types.premium.BoostsList(
        count=1,
        boosts=[],
        users=[],
    )
    client = _Client(result=dummy_list)
    res = await client.get_user_boosts(
        chat_id=12345,
        user_id=67890,
    )

    assert res == dummy_list
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.premium.GetUserBoosts)
    assert isinstance(call.peer, raw.types.InputPeerUser)
    assert call.peer.user_id == 12345
    assert isinstance(call.user_id, raw.types.InputUser)
    assert call.user_id.user_id == 67890


def test_client_has_premium_methods():
    assert hasattr(pyrogram.Client, "get_boosts_list")
    assert hasattr(pyrogram.Client, "get_user_boosts")
