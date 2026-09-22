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
        return raw.types.InputPeerChannel(channel_id=uid, access_hash=0)


@pytest.mark.asyncio
async def test_get_ephemeral_callback_answer_dispatches_query():
    from pyrogram.methods.ephemeral.get_ephemeral_callback_answer import GetEphemeralCallbackAnswer

    class _Client(_Recorder, GetEphemeralCallbackAnswer):
        pass

    dummy_answer = raw.types.messages.BotCallbackAnswer(
        alert=False,
        has_url=False,
        native_ui=False,
        message="test answer",
        cache_time=60,
    )
    client = _Client(result=dummy_answer)
    res = await client.get_ephemeral_callback_answer(12345, 999, data=b"click_btn")

    assert res == dummy_answer
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.ephemeral.GetCallbackAnswer)
    assert isinstance(call.peer, raw.types.InputPeerChannel)
    assert call.peer.channel_id == 12345
    assert call.id == 999
    assert call.data == b"click_btn"


@pytest.mark.asyncio
async def test_get_ephemeral_callback_answer_with_str_data():
    from pyrogram.methods.ephemeral.get_ephemeral_callback_answer import GetEphemeralCallbackAnswer

    class _Client(_Recorder, GetEphemeralCallbackAnswer):
        pass

    client = _Client(result=True)
    await client.get_ephemeral_callback_answer(12345, 999, data="click_str")

    assert len(client.calls) == 1
    call = client.calls[0]
    assert call.data == b"click_str"


@pytest.mark.asyncio
async def test_report_ephemeral_message_dispatches_query():
    from pyrogram.methods.ephemeral.report_ephemeral_message import ReportEphemeralMessage

    class _Client(_Recorder, ReportEphemeralMessage):
        pass

    dummy_result = raw.types.ReportResultReported()
    client = _Client(result=dummy_result)
    res = await client.report_ephemeral_message(
        chat_id=12345,
        message_id=999,
        option=b"spam",
        message="This is spam",
    )

    assert res == dummy_result
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.ephemeral.ReportMessage)
    assert isinstance(call.peer, raw.types.InputPeerChannel)
    assert call.peer.channel_id == 12345
    assert call.id == 999
    assert call.option == b"spam"
    assert call.message == "This is spam"


@pytest.mark.asyncio
async def test_report_ephemeral_message_with_str_option():
    from pyrogram.methods.ephemeral.report_ephemeral_message import ReportEphemeralMessage

    class _Client(_Recorder, ReportEphemeralMessage):
        pass

    client = _Client(result=True)
    await client.report_ephemeral_message(12345, 999, option="violence")

    assert len(client.calls) == 1
    call = client.calls[0]
    assert call.option == b"violence"
    assert call.message == ""


def test_client_has_ephemeral_methods():
    assert hasattr(pyrogram.Client, "get_ephemeral_callback_answer")
    assert hasattr(pyrogram.Client, "report_ephemeral_message")
