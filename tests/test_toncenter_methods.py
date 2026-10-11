import pytest

from pyrogram import raw
from pyrogram.methods.toncenter import (
    GetStreamingUrl,
    PerformApiRequest,
)


class _Recorder:
    def __init__(self, result=True):
        self.calls = []
        self.result = result

    async def invoke(self, query, *args, **kwargs):
        self.calls.append(query)
        return self.result


@pytest.mark.asyncio
async def test_perform_api_request_dispatches_query():
    class _Client(_Recorder, PerformApiRequest):
        pass

    client = _Client()
    await client.perform_api_request(
        endpoint="getAddressInformation",
        query="address=EQ123",
        payload='{"key": "value"}',
        post=True,
    )

    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.toncenter.PerformApiRequest)
    assert call.endpoint == "getAddressInformation"
    assert call.query == "address=EQ123"
    assert call.payload == '{"key": "value"}'
    assert call.post is True


@pytest.mark.asyncio
async def test_get_streaming_url_dispatches_query():
    class _Client(_Recorder, GetStreamingUrl):
        pass

    client = _Client()
    await client.get_streaming_url()

    assert len(client.calls) == 1
    assert isinstance(client.calls[0], raw.functions.toncenter.GetStreamingUrl)
