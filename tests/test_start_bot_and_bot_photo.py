from unittest.mock import Mock

import pytest

import pyrogram
from pyrogram import raw, types


class FakeClient:
    def __init__(self, result=True):
        self.sent = None
        self.result = result
        self.messages = []
        self.saved = []
        self.me = Mock(id=999, is_bot=False, is_premium=False)
        self.message_cache = {}
        self.parse_mode = None

    async def invoke(self, query, **kwargs):
        self.sent = query
        return self.result

    async def resolve_peer(self, chat_id):
        return raw.types.InputPeerUser(user_id=777, access_hash=42)

    async def save_file(self, path, *args, **kwargs):
        if path is None:
            return None

        self.saved.append(path)
        return raw.types.InputFile(id=1, parts=1, name=str(path), md5_checksum="")

    async def send_message(self, chat_id, text, *args, **kwargs):
        self.messages.append((chat_id, text))
        return "sent"

    def rnd_id(self):
        return 12345

    async def start_bot(self, chat_id, param=""):
        return await pyrogram.Client.start_bot(self, chat_id, param)

    async def set_bot_profile_photo(self, bot_user_id, **kwargs):
        return await pyrogram.Client.set_bot_profile_photo(self, bot_user_id, **kwargs)


@pytest.fixture
def client():
    return FakeClient()


def bot_user():
    return raw.types.User(
        id=777,
        first_name="Bot",
        bot=True,
        usernames=[],
        restriction_reason=[],
        access_hash=42,
    )


def updates(*update_list):
    return raw.types.Updates(updates=list(update_list), users=[bot_user()], chats=[], date=0, seq=0)


def raw_message(message_id=55):
    return raw.types.Message(
        id=message_id,
        peer_id=raw.types.PeerUser(user_id=777),
        from_id=raw.types.PeerUser(user_id=777),
        date=1700000000,
        restriction_reason=[],
        message="hi",
        entities=[],
    )


async def test_start_bot_without_a_param_sends_the_plain_command(client):
    assert await client.start_bot("tobigrambot") == "sent"
    assert client.messages == [("tobigrambot", "/start")]
    assert client.sent is None


async def test_start_bot_with_a_param_invokes_start_bot(client):
    client.result = updates()

    await client.start_bot("tobigrambot", "ref123456")

    assert isinstance(client.sent, raw.functions.messages.StartBot)
    assert client.sent.start_param == "ref123456"
    assert client.sent.random_id == 12345
    assert client.sent.bot == client.sent.peer
    assert client.sent.bot.user_id == 777
    assert not client.messages


async def test_start_bot_returns_the_message_the_server_sent(client):
    client.result = updates(raw.types.UpdateNewMessage(message=raw_message(), pts=1, pts_count=1))

    message = await client.start_bot("tobigrambot", "ref123456")

    assert isinstance(message, types.Message)
    assert message.id == 55


async def test_start_bot_returns_none_when_no_message_arrives(client):
    client.result = updates(raw.types.UpdateMessageID(id=1, random_id=12345))

    assert await client.start_bot("tobigrambot", "ref123456") is None


async def test_set_bot_profile_photo_uploads_a_photo_for_that_bot(client):
    assert await client.set_bot_profile_photo("tobigrambot", photo="new.jpg") is True

    assert isinstance(client.sent, raw.functions.photos.UploadProfilePhoto)
    assert client.sent.bot.user_id == 777
    assert client.sent.file is not None
    assert client.sent.video is None
    assert client.saved == ["new.jpg"]


async def test_set_bot_profile_photo_uploads_a_video_for_that_bot(client):
    assert await client.set_bot_profile_photo("tobigrambot", video="new.mp4") is True

    assert isinstance(client.sent, raw.functions.photos.UploadProfilePhoto)
    assert client.sent.file is None
    assert client.sent.video is not None
    assert client.saved == ["new.mp4"]


async def test_set_bot_profile_photo_with_neither_removes_the_photo(client):
    assert await client.set_bot_profile_photo("tobigrambot") is True

    assert isinstance(client.sent, raw.functions.photos.UpdateProfilePhoto)
    assert isinstance(client.sent.id, raw.types.InputPhotoEmpty)
    assert client.sent.bot.user_id == 777
    assert client.saved == []


async def test_removing_a_bot_photo_never_uploads_anything(client):
    await client.set_bot_profile_photo("tobigrambot")

    assert not hasattr(client.sent, "file")
