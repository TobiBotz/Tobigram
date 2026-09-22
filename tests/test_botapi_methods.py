import pytest

import pyrogram
from pyrogram import raw, types
from pyrogram.methods.messages.copy_messages import CopyMessages


class _Recorder:
    def __init__(self, result=True):
        self.calls = []
        self.result = result

    async def invoke(self, query, *args, **kwargs):
        self.calls.append((query, kwargs))
        return self.result

    async def resolve_peer(self, peer_id):
        if peer_id == "me" or peer_id == 111:
            return raw.types.InputPeerSelf()
        return raw.types.InputPeerChannel(
            channel_id=int(peer_id) if isinstance(peer_id, int) else 999,
            access_hash=123,
        )


@pytest.mark.asyncio
async def test_verify_user_and_chat():
    from pyrogram.methods.chats.verify_user import VerifyUser
    from pyrogram.methods.chats.verify_chat import VerifyChat

    class _Client(_Recorder, VerifyUser, VerifyChat):
        pass

    client = _Client()
    await client.verify_user(123, custom_description="Gold User")
    call1 = client.calls[0][0]
    assert isinstance(call1, raw.functions.bots.SetCustomVerification)
    assert call1.enabled is True
    assert call1.custom_description == "Gold User"

    await client.verify_chat(456, custom_description="Official Chat")
    call2 = client.calls[1][0]
    assert isinstance(call2, raw.functions.bots.SetCustomVerification)
    assert call2.enabled is True
    assert call2.custom_description == "Official Chat"


@pytest.mark.asyncio
async def test_remove_user_and_chat_verification():
    from pyrogram.methods.chats.remove_user_verification import RemoveUserVerification
    from pyrogram.methods.chats.remove_chat_verification import RemoveChatVerification

    class _Client(_Recorder, RemoveUserVerification, RemoveChatVerification):
        pass

    client = _Client()
    await client.remove_user_verification(123)
    call1 = client.calls[0][0]
    assert isinstance(call1, raw.functions.bots.SetCustomVerification)
    assert call1.enabled is False

    await client.remove_chat_verification(456)
    call2 = client.calls[1][0]
    assert isinstance(call2, raw.functions.bots.SetCustomVerification)
    assert call2.enabled is False


@pytest.mark.asyncio
async def test_set_and_delete_chat_sticker_set():
    from pyrogram.methods.chats.set_chat_sticker_set import SetChatStickerSet
    from pyrogram.methods.chats.delete_chat_sticker_set import DeleteChatStickerSet

    class _Client(_Recorder, SetChatStickerSet, DeleteChatStickerSet):
        pass

    client = _Client()
    await client.set_chat_sticker_set(123, "my_stickers")
    call1 = client.calls[0][0]
    assert isinstance(call1, raw.functions.channels.SetStickers)
    assert isinstance(call1.stickerset, raw.types.InputStickerSetShortName)
    assert call1.stickerset.short_name == "my_stickers"

    await client.delete_chat_sticker_set(123)
    call2 = client.calls[1][0]
    assert isinstance(call2, raw.functions.channels.SetStickers)
    assert isinstance(call2.stickerset, raw.types.InputStickerSetEmpty)


@pytest.mark.asyncio
async def test_business_methods():
    from pyrogram.methods.business.read_business_message import ReadBusinessMessage
    from pyrogram.methods.business.set_business_account_bio import SetBusinessAccountBio
    from pyrogram.methods.business.set_business_account_name import SetBusinessAccountName
    from pyrogram.methods.business.set_business_account_username import SetBusinessAccountUsername

    class _Client(
        _Recorder,
        ReadBusinessMessage,
        SetBusinessAccountBio,
        SetBusinessAccountName,
        SetBusinessAccountUsername,
    ):
        pass

    client = _Client()
    await client.read_business_message("conn123", 123, 456)
    call1, kw1 = client.calls[0]
    assert isinstance(call1, raw.functions.messages.ReadHistory)
    assert kw1.get("business_connection_id") == "conn123"

    await client.set_business_account_bio("conn123", "Bio text")
    call2, kw2 = client.calls[1]
    assert isinstance(call2, raw.functions.account.UpdateProfile)
    assert call2.about == "Bio text"
    assert kw2.get("business_connection_id") == "conn123"

    await client.set_business_account_name("conn123", "First", "Last")
    call3, kw3 = client.calls[2]
    assert isinstance(call3, raw.functions.account.UpdateProfile)
    assert call3.first_name == "First"
    assert call3.last_name == "Last"
    assert kw3.get("business_connection_id") == "conn123"

    await client.set_business_account_username("conn123", "uname")
    call4, kw4 = client.calls[3]
    assert isinstance(call4, raw.functions.account.UpdateUsername)
    assert call4.username == "uname"
    assert kw4.get("business_connection_id") == "conn123"


@pytest.mark.asyncio
async def test_copy_messages():
    class _DummyMessage:
        def __init__(self, val):
            self.val = val

        async def copy(self, *args, **kwargs):
            return f"copied_{self.val}"

    class _Client(_Recorder, CopyMessages):
        async def get_messages(self, chat_id, message_ids):
            return [_DummyMessage("1"), _DummyMessage("2")]

    client = _Client()
    res = await client.copy_messages(chat_id=123, from_chat_id=456, message_ids=[1, 2])
    assert res == ["copied_1", "copied_2"]
