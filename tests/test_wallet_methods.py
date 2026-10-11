import pytest

from pyrogram import raw, types
from pyrogram.methods.wallet import (
    AcceptTonConnectRequest,
    CreateUserWallet,
    CreateWallet,
    DeclineTonConnectRequest,
    DisconnectTonConnectSession,
    DisableWalletBackup,
    EnableWalletBackup,
    ExportWalletSecretPhrase,
    FetchEncryptedSecretPhrasePart,
    GetBackupHolderDcs,
    GetExistingWalletBalance,
    GetTonConnectNextEventId,
    GetTonConnectPending,
    GetTonConnectSessions,
    GetUserWalletAddresses,
    GetProofChallenge,
    GetWalletGaslessInfo,
    GetWalletNfts,
    GetWalletState,
    GetWalletTransactions,
    GetWalletTransactionsByIds,
    GetWalletTransactionsByMsgHash,
    ImportWallet,
    RegisterTonConnectKey,
    ReplaceWallet,
    SendTonTransfer,
    StartTonConnectSession,
    SubmitTonConnectResponse,
    SubmitTonConnectResult,
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

    dummy_state = raw.types.WalletState(
        address="EQA...",
        public_key=b"pubkey",
        balance=1000000000,
        backup_enabled=True,
    )
    client = _Client(result=dummy_state)
    res = await client.get_wallet_state()

    assert len(client.calls) == 1
    assert isinstance(client.calls[0], raw.functions.wallet.GetState)
    assert isinstance(res, types.WalletState)
    assert res.address == "EQA..."
    assert res.balance_ton == 1.0
    assert res.backup_enabled is True


@pytest.mark.asyncio
async def test_get_wallet_transactions_dispatches_query():
    class _Client(_Recorder, GetWalletTransactions):
        pass

    dummy_tx = raw.types.WalletTransaction(
        id="tx_123",
        amount=5000000000,
        fee=10000000,
        date=1700000000,
        peer=raw.types.WalletTransactionPeerAddress(address="EQ_peer", domain="peer.ton"),
        incoming=True,
    )
    dummy_res = raw.types.wallet.Transactions(balance=1000, transactions=[dummy_tx], chats=[], users=[])

    client = _Client(result=dummy_res)
    res = await client.get_wallet_transactions(offset="tx_123", limit=50, inbound=True, outbound=False)

    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.wallet.GetTransactions)
    assert call.offset == "tx_123"
    assert call.limit == 50
    assert call.inbound is True
    assert call.outbound is False
    assert len(res) == 1
    assert isinstance(res[0], types.WalletTransaction)
    assert res[0].id == "tx_123"
    assert res[0].amount_ton == 5.0
    assert res[0].is_incoming is True
    assert res[0].peer_address == "EQ_peer"


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

    dummy_gasless = raw.types.UpdateWalletGaslessInfo(
        available=True,
        left=5,
        reset_at=1700000000,
        min_amount=1000000000,
        relayer_address="EQ_relayer",
    )
    dummy_updates = raw.types.Updates(updates=[dummy_gasless], users=[], chats=[], date=1700000000, seq=0)

    client = _Client(result=dummy_updates)
    res = await client.get_wallet_gasless_info()

    assert len(client.calls) == 1
    assert isinstance(client.calls[0], raw.functions.wallet.GetGaslessInfo)
    assert isinstance(res, types.WalletGaslessInfo)
    assert res.is_available is True
    assert res.transfers_left == 5
    assert res.min_amount_ton == 1.0
    assert res.relayer_address == "EQ_relayer"


@pytest.mark.asyncio
async def test_get_user_wallet_addresses_dispatches_query():
    dummy_user_address = raw.types.WalletUserAddress(
        user_id=111,
        address="EQ_addr",
        public_key=b"pubkey",
    )
    dummy_user = raw.types.User(id=111, access_hash=123, first_name="Bob")
    dummy_res = raw.types.wallet.UserAddresses(
        addresses=[dummy_user_address],
        users=[dummy_user],
    )

    class _Client(_Recorder, GetUserWalletAddresses):
        pass

    client = _Client(result=dummy_res)
    res = await client.get_user_wallet_addresses(users=[111, 222], addresses=["EQ_addr"], force=True)

    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.wallet.GetUserAddresses)
    assert len(call.id) == 2
    assert call.addresses == ["EQ_addr"]
    assert call.force is True
    assert len(res) == 1
    assert isinstance(res[0], types.UserTonWalletAddress)
    assert res[0].wallet_address == "EQ_addr"
    assert res[0].user.first_name == "Bob"


@pytest.mark.asyncio
async def test_get_existing_wallet_balance_dispatches_query():
    class _Client(_Recorder, GetExistingWalletBalance):
        pass

    client = _Client()
    await client.get_existing_wallet_balance()

    assert len(client.calls) == 1
    assert isinstance(client.calls[0], raw.functions.wallet.GetExistingWaltBalance)


@pytest.mark.asyncio
async def test_send_ton_transfer_dispatches_query():
    class _Client(_Recorder, SendTonTransfer):
        pass

    client = _Client()
    await client.send_ton_transfer(
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

    # Test backward compatibility alias
    await client.send_wallet_transfer(
        user_id=222,
        data_normal=b"payload_bytes",
    )
    assert len(client.calls) == 2


@pytest.mark.asyncio
async def test_get_ton_connect_sessions_dispatches_query():
    class _Client(_Recorder, GetTonConnectSessions):
        pass

    dummy_session = raw.types.TonConnectSession(
        id=101,
        dapp_client_id="dapp",
        client_id="cid",
        nonce=b"nonce",
        date=1700000000,
        manifest=raw.types.TonConnectManifest(
            url="https://manifest",
            name="TestDApp",
        ),
    )
    dummy_res = raw.types.wallet.TonConnectSessions(sessions=[dummy_session])

    client = _Client(result=dummy_res)
    res = await client.get_ton_connect_sessions()

    assert len(client.calls) == 1
    assert isinstance(client.calls[0], raw.functions.wallet.TonConnectGetSessions)
    assert len(res) == 1
    assert isinstance(res[0], types.TonConnectSession)
    assert res[0].id == 101
    assert res[0].manifest_name == "TestDApp"


@pytest.mark.asyncio
async def test_get_wallet_transactions_by_ids_dispatches_query():
    class _Client(_Recorder, GetWalletTransactionsByIds):
        pass

    dummy_tx = raw.types.WalletTransaction(
        id="tx_1",
        amount=1000000000,
        fee=5000000,
        date=1700000000,
        peer=raw.types.WalletTransactionPeerAddress(address="EQ_addr"),
    )
    dummy_res = raw.types.wallet.Transactions(balance=1000, transactions=[dummy_tx], chats=[], users=[])

    client = _Client(result=dummy_res)
    res = await client.get_wallet_transactions_by_ids(ids=["tx_1", "tx_2"])

    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.wallet.GetTransactionsByIDs)
    assert call.id == ["tx_1", "tx_2"]
    assert len(res) == 1
    assert isinstance(res[0], types.WalletTransaction)
    assert res[0].id == "tx_1"


@pytest.mark.asyncio
async def test_get_wallet_transactions_by_msg_hash_dispatches_query():
    class _Client(_Recorder, GetWalletTransactionsByMsgHash):
        pass

    dummy_tx = raw.types.WalletTransaction(
        id="tx_h",
        amount=2000000000,
        fee=5000000,
        date=1700000000,
        peer=raw.types.WalletTransactionPeerAddress(address="EQ_addr"),
    )
    dummy_res = raw.types.wallet.Transactions(balance=1000, transactions=[dummy_tx], chats=[], users=[])

    client = _Client(result=dummy_res)
    res = await client.get_wallet_transactions_by_msg_hash(msg_hashes=["hash_1"])

    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.wallet.GetTransactionsByMsgHash)
    assert call.msg_hash == ["hash_1"]
    assert len(res) == 1
    assert isinstance(res[0], types.WalletTransaction)
    assert res[0].id == "tx_h"


@pytest.mark.asyncio
async def test_get_proof_challenge_dispatches_query():
    class _Client(_Recorder, GetProofChallenge):
        pass

    client = _Client()
    await client.get_proof_challenge()

    assert len(client.calls) == 1
    assert isinstance(client.calls[0], raw.functions.wallet.GetProofChallenge)


@pytest.mark.asyncio
async def test_export_wallet_secret_phrase_dispatches_query():
    class _Client(_Recorder, ExportWalletSecretPhrase):
        async def check_password(self, password):
            return raw.types.InputCheckPasswordEmpty()

    client = _Client()
    await client.export_wallet_secret_phrase(password="secret")

    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.wallet.ExportSecretPhrase)
    assert isinstance(call.password, raw.types.InputCheckPasswordEmpty)


@pytest.mark.asyncio
async def test_fetch_encrypted_secret_phrase_part_dispatches_query():
    class _Client(_Recorder, FetchEncryptedSecretPhrasePart):
        pass

    client = _Client()
    await client.fetch_encrypted_secret_phrase_part(token="tok", public_key=b"pub")

    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.wallet.FetchEncryptedSecretPhrasePart)
    assert call.token == "tok"
    assert call.public_key == b"pub"


@pytest.mark.asyncio
async def test_replace_wallet_dispatches_query():
    class _Client(_Recorder, ReplaceWallet):
        pass

    dummy_state = raw.types.WalletState(
        address="EQA...",
        public_key=b"pubkey",
        balance=1000,
    )

    client = _Client(result=dummy_state)
    wallet_repl = raw.types.InputWalletNew()
    res = await client.replace_wallet(wallet=wallet_repl)

    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.wallet.ReplaceWallet)
    assert call.wallet == wallet_repl
    assert isinstance(res, types.WalletState)
    assert res.address == "EQA..."


@pytest.mark.asyncio
async def test_disable_wallet_backup_dispatches_query():
    class _Client(_Recorder, DisableWalletBackup):
        pass

    dummy_state = raw.types.WalletState(
        address="EQA...",
        public_key=b"pubkey",
        balance=1000,
    )

    client = _Client(result=dummy_state)
    res = await client.disable_wallet_backup(new_public_key=b"new_pub")

    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.wallet.DisableBackup)
    assert call.new_public_key == b"new_pub"
    assert isinstance(res, types.WalletState)
    assert res.address == "EQA..."


@pytest.mark.asyncio
async def test_get_backup_holder_dcs_dispatches_query():
    class _Client(_Recorder, GetBackupHolderDcs):
        pass

    client = _Client()
    await client.get_backup_holder_dcs()

    assert len(client.calls) == 1
    assert isinstance(client.calls[0], raw.functions.wallet.GetBackupHolderDcs)


@pytest.mark.asyncio
async def test_enable_wallet_backup_dispatches_query():
    class _Client(_Recorder, EnableWalletBackup):
        pass

    dummy_state = raw.types.WalletState(
        address="EQA...",
        public_key=b"pubkey",
        balance=1000,
    )

    client = _Client(result=dummy_state)
    res = await client.enable_wallet_backup(parts=[b"part1", b"part2"])

    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.wallet.EnableBackup)
    assert call.parts == [b"part1", b"part2"]
    assert isinstance(res, types.WalletState)
    assert res.address == "EQA..."


@pytest.mark.asyncio
async def test_start_ton_connect_session_dispatches_query():
    class _Client(_Recorder, StartTonConnectSession):
        pass

    dummy_session = raw.types.TonConnectSession(
        id=101,
        dapp_client_id="dapp",
        client_id="cid",
        nonce=b"nonce",
        date=1700000000,
        manifest=raw.types.TonConnectManifest(
            url="https://manifest",
            name="DApp",
        ),
    )

    client = _Client(result=dummy_session)
    res = await client.start_ton_connect_session(dapp_client_id="dapp", manifest_url="https://manifest")

    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.wallet.TonConnectCreateSession)
    assert call.dapp_client_id == "dapp"
    assert call.manifest_url == "https://manifest"
    assert isinstance(res, types.TonConnectSession)
    assert res.id == 101

    # Backward compatibility alias
    res2 = await client.start_ton_connect_session(dapp_client_id="dapp", manifest_url="https://manifest")
    assert len(client.calls) == 2
    assert isinstance(res2, types.TonConnectSession)


@pytest.mark.asyncio
async def test_register_ton_connect_key_dispatches_query():
    class _Client(_Recorder, RegisterTonConnectKey):
        pass

    client = _Client()
    await client.register_ton_connect_key(session_id=101, client_id="cid")

    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.wallet.TonConnectRegisterKey)
    assert call.session_id == 101
    assert call.client_id == "cid"


@pytest.mark.asyncio
async def test_submit_ton_connect_result_dispatches_query():
    class _Client(_Recorder, SubmitTonConnectResult):
        pass

    client = _Client()
    await client.submit_ton_connect_result(
        session_id=101,
        challenge_answer=b"ans",
        body=b"body",
        trace_id="tr_1",
        error=False,
    )

    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.wallet.TonConnectSubmitConnectResult)
    assert call.session_id == 101
    assert call.challenge_answer == b"ans"
    assert call.body == b"body"
    assert call.trace_id == "tr_1"
    assert call.error is False


@pytest.mark.asyncio
async def test_get_ton_connect_pending_dispatches_query():
    class _Client(_Recorder, GetTonConnectPending):
        pass

    client = _Client()
    await client.get_ton_connect_pending(session_id=101)

    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.wallet.TonConnectGetPending)
    assert call.session_id == 101


@pytest.mark.asyncio
async def test_accept_and_decline_ton_connect_request_dispatches_query():
    class _Client(_Recorder, AcceptTonConnectRequest, DeclineTonConnectRequest):
        pass

    client = _Client()
    await client.accept_ton_connect_request(
        session_id=101,
        msg_id=202,
        app_request_id="app_req",
        challenge_answer=b"ans",
    )

    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.wallet.TonConnectClaimRequest)
    assert call.session_id == 101
    assert call.msg_id == 202
    assert call.app_request_id == "app_req"
    assert call.challenge_answer == b"ans"
    assert call.declined is False

    await client.decline_ton_connect_request(
        session_id=101,
        msg_id=202,
        app_request_id="app_req",
    )
    assert len(client.calls) == 2
    call2 = client.calls[1]
    assert isinstance(call2, raw.functions.wallet.TonConnectClaimRequest)
    assert call2.declined is True

    # Test alias
    await client.claim_ton_connect_request(
        session_id=101,
        msg_id=202,
        app_request_id="app_req",
        challenge_answer=b"ans",
    )
    assert len(client.calls) == 3


@pytest.mark.asyncio
async def test_submit_ton_connect_response_dispatches_query():
    class _Client(_Recorder, SubmitTonConnectResponse):
        pass

    client = _Client()
    await client.submit_ton_connect_response(
        session_id=101,
        msg_id=202,
        body=b"resp_body",
        trace_id="tr_2",
    )

    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.wallet.TonConnectSubmitResponse)
    assert call.session_id == 101
    assert call.msg_id == 202
    assert call.body == b"resp_body"
    assert call.trace_id == "tr_2"


@pytest.mark.asyncio
async def test_get_ton_connect_next_event_id_dispatches_query():
    class _Client(_Recorder, GetTonConnectNextEventId):
        pass

    client = _Client()
    await client.get_ton_connect_next_event_id(session_id=101)

    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.wallet.TonConnectNextEventId)
    assert call.session_id == 101


@pytest.mark.asyncio
async def test_disconnect_ton_connect_session_dispatches_query():
    class _Client(_Recorder, DisconnectTonConnectSession):
        pass

    client = _Client()
    await client.disconnect_ton_connect_session(session_id=101, body=b"reason")

    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.wallet.TonConnectCloseSession)
    assert call.session_id == 101
    assert call.body == b"reason"

    # Backward compatibility alias
    await client.close_ton_connect_session(session_id=101, body=b"reason")
    assert len(client.calls) == 2


@pytest.mark.asyncio
async def test_create_user_wallet_dispatches_query():
    dummy_user_address = raw.types.WalletUserAddress(
        user_id=123,
        address="EQB...",
        public_key=b"pubkey",
    )
    dummy_user = raw.types.User(id=123, access_hash=456, first_name="Alice")
    dummy_res = raw.types.wallet.UserAddresses(
        addresses=[dummy_user_address],
        users=[dummy_user],
    )

    class _Client(_Recorder, CreateUserWallet):
        pass

    client = _Client(result=dummy_res)
    res = await client.create_user_wallet("alice")

    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.wallet.GetUserAddresses)
    assert call.force is True
    assert res is not None
    assert res.wallet_address == "EQB..."
    assert res.public_key == b"pubkey"
    assert res.user.first_name == "Alice"


@pytest.mark.asyncio
async def test_create_wallet_dispatches_replace_wallet():
    dummy_state = raw.types.WalletState(
        address="EQA...",
        public_key=b"pubkey",
        balance=1000,
    )

    class _Client(_Recorder, CreateWallet, ReplaceWallet):
        async def check_password(self, password):
            return password

    client = _Client(result=dummy_state)
    res = await client.create_wallet(password="secret")

    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.wallet.ReplaceWallet)
    assert isinstance(call.wallet, raw.types.InputWalletNew)
    assert call.password == "secret"
    assert isinstance(res, types.WalletState)
    assert res.address == dummy_state.address
    assert res.balance == dummy_state.balance


@pytest.mark.asyncio
async def test_import_wallet_dispatches_replace_wallet():
    dummy_state = raw.types.WalletState(
        address="EQA...",
        public_key=b"pubkey",
        balance=1000,
    )
    proof = raw.types.WalletOwnershipProof(timestamp=123, signature=b"sig")

    class _Client(_Recorder, ImportWallet, ReplaceWallet):
        async def check_password(self, password):
            return password

    client = _Client(result=dummy_state)
    res = await client.import_wallet(public_key=b"pubkey", proof=proof)

    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.wallet.ReplaceWallet)
    assert isinstance(call.wallet, raw.types.InputWalletImported)
    assert call.wallet.public_key == b"pubkey"
    assert call.wallet.proof == proof
    assert isinstance(res, types.WalletState)
    assert res.address == dummy_state.address
    assert res.balance == dummy_state.balance
