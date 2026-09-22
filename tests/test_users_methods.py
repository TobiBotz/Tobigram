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
async def test_get_requirements_to_contact_dispatches_single_user():
    from pyrogram.methods.users.get_requirements_to_contact import GetRequirementsToContact

    class _Client(_Recorder, GetRequirementsToContact):
        pass

    dummy_req = [raw.types.RequirementToContactPremium()]
    client = _Client(result=dummy_req)
    res = await client.get_requirements_to_contact(12345)

    assert res == dummy_req
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.users.GetRequirementsToContact)
    assert len(call.id) == 1
    assert isinstance(call.id[0], raw.types.InputUser)
    assert call.id[0].user_id == 12345


@pytest.mark.asyncio
async def test_get_requirements_to_contact_dispatches_multiple_users():
    from pyrogram.methods.users.get_requirements_to_contact import GetRequirementsToContact

    class _Client(_Recorder, GetRequirementsToContact):
        pass

    client = _Client(result=[])
    await client.get_requirements_to_contact([12345, 67890])

    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.users.GetRequirementsToContact)
    assert len(call.id) == 2
    assert call.id[0].user_id == 12345
    assert call.id[1].user_id == 67890


@pytest.mark.asyncio
async def test_get_saved_music_by_id_dispatches_query():
    from pyrogram.methods.users.get_saved_music_by_id import GetSavedMusicByID

    class _Client(_Recorder, GetSavedMusicByID):
        pass

    dummy_music = raw.types.users.SavedMusic(
        count=1,
        documents=[],
    )
    client = _Client(result=dummy_music)
    dummy_doc = raw.types.InputDocument(id=111, access_hash=222, file_reference=b"ref")
    res = await client.get_saved_music_by_id(12345, documents=[dummy_doc])

    assert res == dummy_music
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.users.GetSavedMusicByID)
    assert isinstance(call.id, raw.types.InputUser)
    assert call.id.user_id == 12345
    assert call.documents == [dummy_doc]


@pytest.mark.asyncio
async def test_set_secure_value_errors_dispatches_query():
    from pyrogram.methods.users.set_secure_value_errors import SetSecureValueErrors

    class _Client(_Recorder, SetSecureValueErrors):
        pass

    client = _Client(result=True)
    dummy_error = raw.types.SecureValueError(
        type=raw.types.SecureValueTypePersonalDetails(),
        hash=b"err_hash",
        text="Invalid name",
    )
    res = await client.set_secure_value_errors(12345, errors=[dummy_error])

    assert res is True
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.users.SetSecureValueErrors)
    assert isinstance(call.id, raw.types.InputUser)
    assert call.id.user_id == 12345
    assert call.errors == [dummy_error]


def test_client_has_users_methods():
    assert hasattr(pyrogram.Client, "get_requirements_to_contact")
    assert hasattr(pyrogram.Client, "get_saved_music_by_id")
    assert hasattr(pyrogram.Client, "set_secure_value_errors")
