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
async def test_get_collectible_info_username_str():
    from pyrogram.methods.advanced.get_collectible_info import GetCollectibleInfo

    class _Client(_Recorder, GetCollectibleInfo):
        pass

    dummy_info = raw.types.fragment.CollectibleInfo(
        purchase_date=0,
        currency="TON",
        amount=1000,
        crypto_currency="TON",
        crypto_amount=1000,
        url="https://fragment.com/username/test",
    )
    client = _Client(result=dummy_info)
    res = await client.get_collectible_info("@durov")

    assert res == dummy_info
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.fragment.GetCollectibleInfo)
    assert isinstance(call.collectible, raw.types.InputCollectibleUsername)
    assert call.collectible.username == "durov"


@pytest.mark.asyncio
async def test_get_collectible_info_phone_str():
    from pyrogram.methods.advanced.get_collectible_info import GetCollectibleInfo

    class _Client(_Recorder, GetCollectibleInfo):
        pass

    client = _Client(result=True)
    await client.get_collectible_info("+88812345678")

    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call.collectible, raw.types.InputCollectiblePhone)
    assert call.collectible.phone == "88812345678"


@pytest.mark.asyncio
async def test_get_collectible_info_raw_object():
    from pyrogram.methods.advanced.get_collectible_info import GetCollectibleInfo

    class _Client(_Recorder, GetCollectibleInfo):
        pass

    obj = raw.types.InputCollectibleUsername(username="custom")
    client = _Client(result=True)
    await client.get_collectible_info(obj)

    assert len(client.calls) == 1
    call = client.calls[0]
    assert call.collectible == obj


def test_client_has_fragment_methods():
    assert hasattr(pyrogram.Client, "get_collectible_info")
