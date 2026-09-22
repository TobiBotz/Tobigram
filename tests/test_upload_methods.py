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


@pytest.mark.asyncio
async def test_get_file_hashes_dispatches_query():
    from pyrogram.methods.advanced.get_file_hashes import GetFileHashes

    class _Client(_Recorder, GetFileHashes):
        pass

    dummy_hashes = [raw.types.FileHash(offset=0, limit=1024, hash=b"hash123")]
    client = _Client(result=dummy_hashes)
    dummy_location = raw.types.InputDocumentFileLocation(
        id=1,
        access_hash=2,
        file_reference=b"ref",
        thumb_size="",
    )
    res = await client.get_file_hashes(location=dummy_location, offset=1024)

    assert res == dummy_hashes
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.upload.GetFileHashes)
    assert call.location == dummy_location
    assert call.offset == 1024


@pytest.mark.asyncio
async def test_get_web_file_dispatches_query():
    from pyrogram.methods.advanced.get_web_file import GetWebFile

    class _Client(_Recorder, GetWebFile):
        pass

    dummy_web_file = raw.types.upload.WebFile(
        size=100,
        mime_type="image/jpeg",
        file_type=raw.types.storage.FilePartial(),
        mtime=0,
        bytes=b"bytes",
    )
    client = _Client(result=dummy_web_file)
    dummy_location = raw.types.InputWebFileLocation(
        url="https://example.com/img.jpg", access_hash=0
    )
    res = await client.get_web_file(location=dummy_location, offset=0, limit=4096)

    assert res == dummy_web_file
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.upload.GetWebFile)
    assert call.location == dummy_location
    assert call.offset == 0
    assert call.limit == 4096


def test_client_has_upload_methods():
    assert hasattr(pyrogram.Client, "get_file_hashes")
    assert hasattr(pyrogram.Client, "get_web_file")
