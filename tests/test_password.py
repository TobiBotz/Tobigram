import pytest
from pyrogram import Client, raw


class FakePasswordClient(Client):
    def __init__(self):
        super().__init__("test_session", api_id=12345, api_hash="0123456789abcdef0123456789abcdef")
        self.invoked = []
        self._returns = []

    def set_returns(self, returns):
        self._returns = list(returns)

    async def invoke(self, query):
        self.invoked.append(query)
        if self._returns:
            val = self._returns.pop(0)
            if isinstance(val, Exception):
                raise val
            return val
        return True


@pytest.fixture
def client():
    return FakePasswordClient()


class FakePasswordResponse:
    def __init__(self, has_password):
        self.has_password = has_password


@pytest.mark.asyncio
async def test_enable_cloud_password_already_enabled(client):
    client.set_returns([FakePasswordResponse(has_password=True)])
    with pytest.raises(ValueError, match="already a cloud password enabled"):
        await client.enable_cloud_password("my_new_pass")


@pytest.mark.asyncio
async def test_change_cloud_password_no_password(client):
    client.set_returns([FakePasswordResponse(has_password=False)])
    with pytest.raises(ValueError, match="no cloud password to change"):
        await client.change_cloud_password("old_pass", "new_pass")


@pytest.mark.asyncio
async def test_remove_cloud_password_no_password(client):
    client.set_returns([FakePasswordResponse(has_password=False)])
    with pytest.raises(ValueError, match="no cloud password to remove"):
        await client.remove_cloud_password("my_pass")


@pytest.mark.asyncio
async def test_remove_cloud_password_success(client):
    algo = raw.types.PasswordKdfAlgoSHA256SHA256PBKDF2HMACSHA512iter100000SHA256ModPow(
        salt1=b"0" * 32,
        salt2=b"1" * 32,
        g=3,
        p=b"\x07" * 256,
    )
    client.set_returns(
        [
            raw.types.account.Password(
                has_password=True,
                current_algo=algo,
                srp_B=b"\x05" * 256,
                srp_id=12345,
                new_algo=algo,
                new_secure_algo=raw.types.SecurePasswordKdfAlgoUnknown(),
                secure_random=b"0" * 256,
            ),
            True,
        ]
    )
    res = await client.remove_cloud_password("my_pass")
    assert res is True
    assert len(client.invoked) == 2
    req = client.invoked[-1]
    assert isinstance(req, raw.functions.account.UpdatePasswordSettings)
    assert isinstance(req.password, raw.types.InputCheckPasswordSRP)


@pytest.mark.asyncio
async def test_change_cloud_password_keep_existing_hint(client):
    algo = raw.types.PasswordKdfAlgoSHA256SHA256PBKDF2HMACSHA512iter100000SHA256ModPow(
        salt1=b"0" * 32,
        salt2=b"1" * 32,
        g=3,
        p=b"\x07" * 256,
    )
    client.set_returns(
        [
            raw.types.account.Password(
                has_password=True,
                current_algo=algo,
                srp_B=b"\x05" * 256,
                srp_id=12345,
                new_algo=algo,
                new_secure_algo=raw.types.SecurePasswordKdfAlgoUnknown(),
                secure_random=b"0" * 256,
                hint="existing_hint",
            ),
            True,
        ]
    )
    res = await client.change_cloud_password("old_pass", "new_pass")
    assert res is True
    req = client.invoked[-1]
    assert isinstance(req, raw.functions.account.UpdatePasswordSettings)
    assert req.new_settings.hint == "existing_hint"


@pytest.mark.asyncio
async def test_enable_cloud_password_success(client):
    algo = raw.types.PasswordKdfAlgoSHA256SHA256PBKDF2HMACSHA512iter100000SHA256ModPow(
        salt1=b"0" * 32,
        salt2=b"1" * 32,
        g=3,
        p=b"\x07" * 256,
    )
    client.set_returns(
        [
            raw.types.account.Password(
                has_password=False,
                current_algo=algo,
                srp_B=b"\x05" * 256,
                srp_id=12345,
                new_algo=algo,
                new_secure_algo=raw.types.SecurePasswordKdfAlgoUnknown(),
                secure_random=b"0" * 256,
            ),
            True,
        ]
    )
    res = await client.enable_cloud_password(
        "my_new_pass", hint="my_hint", email="test@example.com"
    )
    assert res is True
    assert len(client.invoked) == 2
    req = client.invoked[-1]
    assert isinstance(req, raw.functions.account.UpdatePasswordSettings)
    assert req.new_settings.hint == "my_hint"
    assert req.new_settings.email == "test@example.com"


@pytest.mark.asyncio
async def test_change_cloud_password_custom_new_hint(client):
    algo = raw.types.PasswordKdfAlgoSHA256SHA256PBKDF2HMACSHA512iter100000SHA256ModPow(
        salt1=b"0" * 32,
        salt2=b"1" * 32,
        g=3,
        p=b"\x07" * 256,
    )
    client.set_returns(
        [
            raw.types.account.Password(
                has_password=True,
                current_algo=algo,
                srp_B=b"\x05" * 256,
                srp_id=12345,
                new_algo=algo,
                new_secure_algo=raw.types.SecurePasswordKdfAlgoUnknown(),
                secure_random=b"0" * 256,
                hint="old_hint",
            ),
            True,
        ]
    )
    res = await client.change_cloud_password("old_pass", "new_pass", new_hint="updated_hint")
    assert res is True
    req = client.invoked[-1]
    assert isinstance(req, raw.functions.account.UpdatePasswordSettings)
    assert req.new_settings.hint == "updated_hint"
