import pytest

import pyrogram
from pyrogram import raw


class _Recorder:
    def __init__(self, result=True):
        self.calls = []
        self.result = result
        self.api_id = 12345
        self.api_hash = "abcdef0123456789"

    async def invoke(self, query, *args, **kwargs):
        self.calls.append(query)
        return self.result


@pytest.mark.asyncio
async def test_accept_login_token_dispatches_query():
    from pyrogram.methods.auth.accept_login_token import AcceptLoginToken

    class _Client(_Recorder, AcceptLoginToken):
        pass

    client = _Client(result=True)
    res = await client.accept_login_token(b"token_bytes")

    assert res is True
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.auth.AcceptLoginToken)
    assert call.token == b"token_bytes"


@pytest.mark.asyncio
async def test_export_login_token_dispatches_query():
    from pyrogram.methods.auth.export_login_token import ExportLoginToken

    class _Client(_Recorder, ExportLoginToken):
        pass

    client = _Client(result=True)
    res = await client.export_login_token(except_ids=[111, 222])

    assert res is True
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.auth.ExportLoginToken)
    assert call.api_id == 12345
    assert call.api_hash == "abcdef0123456789"
    assert call.except_ids == [111, 222]


@pytest.mark.asyncio
async def test_import_login_token_dispatches_query():
    from pyrogram.methods.auth.import_login_token import ImportLoginToken

    class _Client(_Recorder, ImportLoginToken):
        pass

    client = _Client(result=True)
    res = await client.import_login_token(b"redirect_token")

    assert res is True
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.auth.ImportLoginToken)
    assert call.token == b"redirect_token"


@pytest.mark.asyncio
async def test_export_authorization_dispatches_query():
    from pyrogram.methods.auth.export_authorization import ExportAuthorization

    class _Client(_Recorder, ExportAuthorization):
        pass

    client = _Client(result=True)
    res = await client.export_authorization(2)

    assert res is True
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.auth.ExportAuthorization)
    assert call.dc_id == 2


@pytest.mark.asyncio
async def test_import_authorization_dispatches_query():
    from pyrogram.methods.auth.import_authorization import ImportAuthorization

    class _Client(_Recorder, ImportAuthorization):
        pass

    client = _Client(result=True)
    res = await client.import_authorization(999, b"auth_bytes")

    assert res is True
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.auth.ImportAuthorization)
    assert call.id == 999
    assert call.bytes == b"auth_bytes"


@pytest.mark.asyncio
async def test_bind_temp_auth_key_dispatches_query():
    from pyrogram.methods.auth.bind_temp_auth_key import BindTempAuthKey

    class _Client(_Recorder, BindTempAuthKey):
        pass

    client = _Client(result=True)
    res = await client.bind_temp_auth_key(
        perm_auth_key_id=111,
        nonce=222,
        expires_at=1700000000,
        encrypted_message=b"enc",
    )

    assert res is True
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.auth.BindTempAuthKey)
    assert call.perm_auth_key_id == 111
    assert call.nonce == 222
    assert call.expires_at == 1700000000
    assert call.encrypted_message == b"enc"


@pytest.mark.asyncio
async def test_drop_temp_auth_keys_dispatches_query():
    from pyrogram.methods.auth.drop_temp_auth_keys import DropTempAuthKeys

    class _Client(_Recorder, DropTempAuthKeys):
        pass

    client = _Client(result=True)
    res = await client.drop_temp_auth_keys([123, 456])

    assert res is True
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.auth.DropTempAuthKeys)
    assert call.except_auth_keys == [123, 456]


@pytest.mark.asyncio
async def test_init_passkey_login_dispatches_query():
    from pyrogram.methods.auth.init_passkey_login import InitPasskeyLogin

    class _Client(_Recorder, InitPasskeyLogin):
        pass

    client = _Client(result=True)
    res = await client.init_passkey_login()

    assert res is True
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.auth.InitPasskeyLogin)
    assert call.api_id == 12345
    assert call.api_hash == "abcdef0123456789"


@pytest.mark.asyncio
async def test_finish_passkey_login_dispatches_query():
    from pyrogram.methods.auth.finish_passkey_login import FinishPasskeyLogin

    class _Client(_Recorder, FinishPasskeyLogin):
        pass

    dummy_credential = raw.types.InputPasskeyCredentialPublicKey(
        id="cred_id",
        raw_id="raw_id",
        response=raw.types.InputPasskeyResponseLogin(
            client_data=raw.types.DataJSON(data="json"),
            authenticator_data=b"auth",
            signature=b"sig",
            user_handle="2:12345",
        ),
    )

    client = _Client(result=True)
    res = await client.finish_passkey_login(dummy_credential, from_dc_id=2, from_auth_key_id=999)

    assert res is True
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.auth.FinishPasskeyLogin)
    assert call.credential == dummy_credential
    assert call.from_dc_id == 2
    assert call.from_auth_key_id == 999


@pytest.mark.asyncio
async def test_init_firebase_pnv_login_dispatches_query():
    from pyrogram.methods.auth.init_firebase_pnv_login import InitFirebasePnvLogin

    class _Client(_Recorder, InitFirebasePnvLogin):
        pass

    client = _Client(result=True)
    res = await client.init_firebase_pnv_login()

    assert res is True
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.auth.InitFirebasePnvLogin)
    assert call.api_id == 12345
    assert call.api_hash == "abcdef0123456789"


@pytest.mark.asyncio
async def test_finish_firebase_pnv_login_dispatches_query():
    from pyrogram.methods.auth.finish_firebase_pnv_login import FinishFirebasePnvLogin

    class _Client(_Recorder, FinishFirebasePnvLogin):
        pass

    client = _Client(result=True)
    res = await client.finish_firebase_pnv_login("google_tok_123")

    assert res is True
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.auth.FinishFirebasePnvLogin)
    assert call.google_token == "google_tok_123"


@pytest.mark.asyncio
async def test_firebase_pnv_sign_up_dispatches_query():
    from pyrogram.methods.auth.firebase_pnv_sign_up import FirebasePnvSignUp

    class _Client(_Recorder, FirebasePnvSignUp):
        pass

    client = _Client(result=True)
    res = await client.firebase_pnv_sign_up("John", "Doe", no_joined_notifications=True)

    assert res is True
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.auth.FirebasePnvSignUp)
    assert call.first_name == "John"
    assert call.last_name == "Doe"
    assert call.no_joined_notifications is True


@pytest.mark.asyncio
async def test_request_firebase_sms_dispatches_query():
    from pyrogram.methods.auth.request_firebase_sms import RequestFirebaseSms

    class _Client(_Recorder, RequestFirebaseSms):
        pass

    client = _Client(result=True)
    res = await client.request_firebase_sms(
        "+1234567890",
        "hash123",
        safety_net_token="s_token",
        play_integrity_token="p_token",
        ios_push_secret="ios_secret",
    )

    assert res is True
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.auth.RequestFirebaseSms)
    assert call.phone_number == "+1234567890"
    assert call.phone_code_hash == "hash123"
    assert call.safety_net_token == "s_token"
    assert call.play_integrity_token == "p_token"
    assert call.ios_push_secret == "ios_secret"


@pytest.mark.asyncio
async def test_import_web_token_authorization_dispatches_query():
    from pyrogram.methods.auth.import_web_token_authorization import ImportWebTokenAuthorization

    class _Client(_Recorder, ImportWebTokenAuthorization):
        pass

    client = _Client(result=True)
    res = await client.import_web_token_authorization("web_token_xyz")

    assert res is True
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.auth.ImportWebTokenAuthorization)
    assert call.api_id == 12345
    assert call.api_hash == "abcdef0123456789"
    assert call.web_auth_token == "web_token_xyz"


@pytest.mark.asyncio
async def test_cancel_code_dispatches_query():
    from pyrogram.methods.auth.cancel_code import CancelCode

    class _Client(_Recorder, CancelCode):
        pass

    client = _Client(result=True)
    res = await client.cancel_code("+1234567890", "hash123")

    assert res is True
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.auth.CancelCode)
    assert call.phone_number == "+1234567890"
    assert call.phone_code_hash == "hash123"


@pytest.mark.asyncio
async def test_check_paid_auth_dispatches_query():
    from pyrogram.methods.auth.check_paid_auth import CheckPaidAuth

    class _Client(_Recorder, CheckPaidAuth):
        pass

    client = _Client(result=True)
    res = await client.check_paid_auth("+1234567890", "hash123", form_id=777)

    assert res is True
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.auth.CheckPaidAuth)
    assert call.phone_number == "+1234567890"
    assert call.phone_code_hash == "hash123"
    assert call.form_id == 777


@pytest.mark.asyncio
async def test_check_recovery_password_dispatches_query():
    from pyrogram.methods.auth.check_recovery_password import CheckRecoveryPassword

    class _Client(_Recorder, CheckRecoveryPassword):
        pass

    client = _Client(result=True)
    res = await client.check_recovery_password("123456")

    assert res is True
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.auth.CheckRecoveryPassword)
    assert call.code == "123456"


@pytest.mark.asyncio
async def test_report_missing_code_dispatches_query():
    from pyrogram.methods.auth.report_missing_code import ReportMissingCode

    class _Client(_Recorder, ReportMissingCode):
        pass

    client = _Client(result=True)
    res = await client.report_missing_code("+1234567890", "hash123", mnc="01")

    assert res is True
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.auth.ReportMissingCode)
    assert call.phone_number == "+1234567890"
    assert call.phone_code_hash == "hash123"
    assert call.mnc == "01"


@pytest.mark.asyncio
async def test_reset_login_email_dispatches_query():
    from pyrogram.methods.auth.reset_login_email import ResetLoginEmail

    class _Client(_Recorder, ResetLoginEmail):
        pass

    client = _Client(result=True)
    res = await client.reset_login_email("+1234567890", "hash123")

    assert res is True
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.auth.ResetLoginEmail)
    assert call.phone_number == "+1234567890"
    assert call.phone_code_hash == "hash123"


def test_client_has_all_new_auth_methods():
    client_methods = dir(pyrogram.Client)
    expected_methods = [
        "accept_login_token",
        "export_login_token",
        "import_login_token",
        "export_authorization",
        "import_authorization",
        "bind_temp_auth_key",
        "drop_temp_auth_keys",
        "init_passkey_login",
        "finish_passkey_login",
        "init_firebase_pnv_login",
        "finish_firebase_pnv_login",
        "firebase_pnv_sign_up",
        "request_firebase_sms",
        "import_web_token_authorization",
        "cancel_code",
        "check_paid_auth",
        "check_recovery_password",
        "report_missing_code",
        "reset_login_email",
    ]
    for method in expected_methods:
        assert method in client_methods, f"Client is missing method: {method}"
