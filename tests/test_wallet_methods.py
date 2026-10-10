import pytest

from pyrogram import raw
from pyrogram.methods.wallet import (
    GetExistingWalletBalance,
    GetTonConnectSessions,
    GetUserWalletAddresses,
    GetWalletGaslessInfo,
    GetWalletNfts,
    GetWalletState,
    GetWalletTransactions,
    SendWalletTransfer,
)


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
        return raw.types.InputUser(
            user_id=int(peer_id) if isinstance(peer_id, int) else 999,
            access_hash=123,
        )

    def rnd_id(self):
        return 42


@pytest.mark.asyncio
async def test_get_wallet_state_dispatches_query():
    class _Client(_Recorder, GetWalletState):
        pass

    client = _Client()
    await client.get_wallet_state()

    assert len(client.calls) == 1
    assert isinstance(client.calls[0], raw.functions.wallet.GetState)


@pytest.mark.asyncio
async def test_get_wallet_transactions_dispatches_query():
    class _Client(_Recorder, GetWalletTransactions):
        pass

    client = _Client()
    await client.get_wallet_transactions(offset="tx_123", limit=50, inbound=True, outbound=False)

    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.wallet.GetTransactions)
    assert call.offset == "tx_123"
    assert call.limit == 50
    assert call.inbound is True
    assert call.outbound is False


@pytest.mark.asyncio
async def test_get_wallet_nfts_dispatches_query():
    class _Client(_Recorder, GetWalletNfts):
        pass

    client = _Client()
    await client.get_wallet_nfts(offset="nft_off", limit=25)

    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.wallet.GetNfts)
    assert call.offset == "nft_off"
    assert call.limit == 25


@pytest.mark.asyncio
async def test_get_wallet_gasless_info_dispatches_query():
    class _Client(_Recorder, GetWalletGaslessInfo):
        pass

    client = _Client()
    await client.get_wallet_gasless_info()

    assert len(client.calls) == 1
    assert isinstance(client.calls[0], raw.functions.wallet.GetGaslessInfo)


@pytest.mark.asyncio
async def test_get_user_wallet_addresses_dispatches_query():
    class _Client(_Recorder, GetUserWalletAddresses):
        pass

    client = _Client()
    await client.get_user_wallet_addresses(users=[111, 222], addresses=["EQ_addr"], force=True)

    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.wallet.GetUserAddresses)
    assert len(call.id) == 2
    assert call.addresses == ["EQ_addr"]
    assert call.force is True


@pytest.mark.asyncio
async def test_get_existing_wallet_balance_dispatches_query():
    class _Client(_Recorder, GetExistingWalletBalance):
        pass

    client = _Client()
    await client.get_existing_wallet_balance()

    assert len(client.calls) == 1
    assert isinstance(client.calls[0], raw.functions.wallet.GetExistingWaltBalance)


@pytest.mark.asyncio
async def test_send_wallet_transfer_dispatches_query():
    class _Client(_Recorder, SendWalletTransfer):
        pass

    client = _Client()
    await client.send_wallet_transfer(
        user_id=222,
        data_normal=b"payload_bytes",
        data_gasless=b"gasless_bytes",
        random_id=9999,
    )

    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.wallet.SendTransfer)
    assert call.data_normal == b"payload_bytes"
    assert call.data_gasless == b"gasless_bytes"
    assert call.random_id == 9999


@pytest.mark.asyncio
async def test_get_ton_connect_sessions_dispatches_query():
    class _Client(_Recorder, GetTonConnectSessions):
        pass

    client = _Client()
    await client.get_ton_connect_sessions()

    assert len(client.calls) == 1
    assert isinstance(client.calls[0], raw.functions.wallet.TonConnectGetSessions)
