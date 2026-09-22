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
async def test_upload_contact_profile_photo_dispatches_query():
    from pyrogram.methods.contacts.upload_contact_profile_photo import UploadContactProfilePhoto

    class _Client(_Recorder, UploadContactProfilePhoto):
        pass

    dummy_photo = raw.types.photos.Photo(
        photo=raw.types.PhotoEmpty(id=0),
        users=[],
    )
    client = _Client(result=dummy_photo)
    dummy_file = raw.types.InputFile(id=1, parts=1, name="photo.jpg", md5_checksum="md5")
    res = await client.upload_contact_profile_photo(
        user_id=12345,
        photo=dummy_file,
        suggest=True,
        save=False,
    )

    assert res == dummy_photo
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.photos.UploadContactProfilePhoto)
    assert isinstance(call.user_id, raw.types.InputUser)
    assert call.user_id.user_id == 12345
    assert call.file == dummy_file
    assert call.suggest is True
    assert call.save is False


def test_client_has_photos_methods():
    assert hasattr(pyrogram.Client, "upload_contact_profile_photo")
