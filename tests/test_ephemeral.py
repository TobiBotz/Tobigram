import pytest
from pyrogram import Client, raw


class FakeEphemeralClient(Client):
    def __init__(self):
        super().__init__("test_session", api_id=12345, api_hash="0123456789abcdef0123456789abcdef")
        self.invoked = []
        self._invoke_return = True

    def set_return(self, val):
        self._invoke_return = val

    async def invoke(self, query):
        self.invoked.append(query)
        return self._invoke_return

    async def resolve_peer(self, peer_id):
        if isinstance(peer_id, int) or str(peer_id).isdigit():
            return raw.types.InputPeerUser(user_id=int(peer_id), access_hash=789)
        return raw.types.InputPeerSelf()


@pytest.fixture
def client():
    return FakeEphemeralClient()


class DummyCallbackAnswer:
    pass


class DummyReportResult:
    pass


@pytest.mark.asyncio
async def test_send_ephemeral_message(client):
    client.set_return(
        raw.types.Updates(
            updates=[
                raw.types.UpdateNewEphemeralMessage(
                    message=raw.types.EphemeralMessage(
                        id=1,
                        from_id=raw.types.PeerUser(user_id=123),
                        receiver_id=123,
                        date=1700000000,
                        message="hello",
                    ),
                )
            ],
            users=[],
            chats=[],
            date=1700000000,
            seq=1,
        )
    )
    msg = await client.send_ephemeral_message(1001, 2002, "hello")
    assert len(client.invoked) == 1
    req = client.invoked[-1]
    assert isinstance(req, raw.functions.ephemeral.SendMessage)
    assert isinstance(req.receiver_id, raw.types.InputUser)
    assert req.receiver_id.user_id == 2002
    assert msg is not None


@pytest.mark.asyncio
async def test_delete_ephemeral_message(client):
    client.set_return(True)
    res = await client.delete_ephemeral_message(1001, 2002, 10)
    assert res is True
    req = client.invoked[-1]
    assert isinstance(req, raw.functions.ephemeral.DeleteMessage)
    assert isinstance(req.receiver_id, raw.types.InputUser)
    assert req.receiver_id.user_id == 2002


@pytest.mark.asyncio
async def test_delete_welcome_message(client):
    client.set_return(True)
    res = await client.delete_welcome_message(1001, 10)
    assert res is True
    req = client.invoked[-1]
    assert isinstance(req, raw.functions.ephemeral.DeleteWelcomeMessage)


@pytest.mark.asyncio
async def test_delete_all_welcome_messages(client):
    client.set_return(True)
    res = await client.delete_all_welcome_messages(1001)
    assert res is True
    req = client.invoked[-1]
    assert isinstance(req, raw.functions.ephemeral.DeleteAllWelcomeMessages)


@pytest.mark.asyncio
async def test_get_ephemeral_callback_answer(client):
    client.set_return(DummyCallbackAnswer())
    await client.get_ephemeral_callback_answer(1001, 10, "test_data")
    req = client.invoked[-1]
    assert isinstance(req, raw.functions.ephemeral.GetCallbackAnswer)
    assert req.data == b"test_data"


@pytest.mark.asyncio
async def test_report_ephemeral_message(client):
    client.set_return(DummyReportResult())
    await client.report_ephemeral_message(1001, 10, "spam", "Spam msg")
    req = client.invoked[-1]
    assert isinstance(req, raw.functions.ephemeral.ReportMessage)
    assert req.option == b"spam"
