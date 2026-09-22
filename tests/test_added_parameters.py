import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pyrogram
from pyrogram import enums, raw, types, utils

VIEW_ONCE_TTL = (1 << 31) - 1


class FakeClient:
    def __init__(self, answers=None):
        self.sent = []
        self.answers = list(answers or [])
        self.parse_mode = enums.ParseMode.DEFAULT
        self.sleep_threshold = 10

    async def invoke(self, query, *args, **kwargs):
        self.sent.append(query)

        if self.answers:
            return self.answers.pop(0)

        return raw.types.Updates(updates=[], users=[], chats=[], date=0, seq=0)

    async def resolve_peer(self, peer_id):
        if isinstance(peer_id, int) and peer_id < 0:
            return raw.types.InputPeerChannel(channel_id=-peer_id, access_hash=0)

        return raw.types.InputPeerUser(user_id=peer_id or 1, access_hash=0)

    async def save_file(self, *args, **kwargs):
        return raw.types.InputFile(id=1, parts=1, name="f", md5_checksum="")

    def guess_mime_type(self, name):
        return None

    def rnd_id(self):
        return 1


@pytest.fixture
def no_text(monkeypatch):
    async def parse_text_entities(client, text, parse_mode, entities):
        return {"message": text or "", "entities": None}

    async def get_reply_to(*args, **kwargs):
        return None

    monkeypatch.setattr(utils, "parse_text_entities", parse_text_entities)
    monkeypatch.setattr(utils, "get_reply_to", get_reply_to)


@pytest.mark.asyncio
async def test_a_view_once_photo_gets_the_ttl_that_means_view_once(tmp_path, no_text):
    client = FakeClient()
    photo = tmp_path / "p.jpg"
    photo.write_bytes(b"x")

    await pyrogram.Client.send_photo(client, 7, str(photo), view_once=True)

    assert client.sent[0].media.ttl_seconds == VIEW_ONCE_TTL


@pytest.mark.asyncio
async def test_a_voice_carries_its_waveform_and_ttl(tmp_path, no_text):
    client = FakeClient()
    voice = tmp_path / "v.ogg"
    voice.write_bytes(b"x")

    await pyrogram.Client.send_voice(
        client, 7, str(voice), waveform=b"\x01\x02", view_once=True
    )

    media = client.sent[0].media

    assert media.ttl_seconds == VIEW_ONCE_TTL
    assert media.attributes[0].waveform == b"\x01\x02"


@pytest.mark.asyncio
async def test_a_video_note_without_view_once_keeps_no_ttl(tmp_path, no_text):
    client = FakeClient()
    note = tmp_path / "n.mp4"
    note.write_bytes(b"x")

    await pyrogram.Client.send_video_note(client, 7, str(note))

    assert client.sent[0].media.ttl_seconds is None


@pytest.mark.asyncio
async def test_a_sticker_carries_its_emoji_and_caption(tmp_path, monkeypatch):
    client = FakeClient()
    sticker = tmp_path / "s.webp"
    sticker.write_bytes(b"x")

    async def parse_text_entities(client, text, parse_mode, entities):
        return {"message": text, "entities": None}

    async def get_reply_to(*args, **kwargs):
        return None

    monkeypatch.setattr(utils, "parse_text_entities", parse_text_entities)
    monkeypatch.setattr(utils, "get_reply_to", get_reply_to)

    await pyrogram.Client.send_sticker(
        client, 7, str(sticker), emoji="🔥", caption="hi"
    )

    query = client.sent[0]

    assert query.message == "hi"
    assert any(
        isinstance(a, raw.types.DocumentAttributeSticker) and a.alt == "🔥"
        for a in query.media.attributes
    )


@pytest.mark.asyncio
async def test_history_boundaries_reach_the_request(monkeypatch):
    client = FakeClient()

    async def parse_messages(client, messages, replies=1):
        return []

    monkeypatch.setattr(utils, "parse_messages", parse_messages)

    async for _ in pyrogram.Client.get_chat_history(
        client, 7, min_id=10, max_id=20, reverse=True
    ):
        pass

    query = client.sent[0]

    assert (query.min_id, query.max_id) == (9, 21)
    assert query.offset_id == 10


@pytest.mark.asyncio
async def test_a_reversed_chunk_comes_back_oldest_first(monkeypatch):
    from pyrogram.methods.messages import get_chat_history

    made = [types.Message(id=i) for i in (3, 2, 1)]

    async def parse_messages(client, messages, replies=1):
        return list(made)

    monkeypatch.setattr(utils, "parse_messages", parse_messages)

    messages = await get_chat_history.get_chunk(
        client=FakeClient(), chat_id=7, reverse=True
    )

    assert [m.id for m in messages] == [1, 2, 3]


@pytest.mark.asyncio
async def test_search_boundaries_reach_the_request(monkeypatch):
    client = FakeClient()

    async def parse_messages(client, messages, replies=1):
        return []

    monkeypatch.setattr(utils, "parse_messages", parse_messages)

    when = datetime(2026, 9, 1, tzinfo=timezone.utc)

    async for _ in pyrogram.Client.search_messages(
        client, 7, offset_id=5, min_id=1, max_id=9, min_date=when, max_date=when
    ):
        pass

    query = client.sent[0]

    assert (query.offset_id, query.min_id, query.max_id) == (5, 1, 9)
    assert query.min_date == query.max_date == utils.datetime_to_timestamp(when)


@pytest.mark.asyncio
async def test_the_pinned_message_is_asked_for_by_its_own_type(monkeypatch):
    client = FakeClient([raw.types.messages.Messages(
        messages=[], chats=[], users=[], topics=[]
    )])

    async def parse_messages(client, messages, replies=1, business_connection_id=None):
        return types.List()

    monkeypatch.setattr(utils, "parse_messages", parse_messages)

    await pyrogram.Client.get_messages(client, 7, pinned=True)

    assert isinstance(client.sent[0].id[0], raw.types.InputMessagePinned)


@pytest.mark.asyncio
async def test_the_archive_is_a_folder_id(monkeypatch):
    client = FakeClient([raw.types.messages.Dialogs(
        dialogs=[], messages=[], chats=[], users=[]
    )])

    async for _ in pyrogram.Client.get_dialogs(
        client, exclude_pinned=True, from_archive=True
    ):
        pass

    query = client.sent[0]

    assert (query.exclude_pinned, query.folder_id) == (True, 1)


@pytest.mark.asyncio
async def test_banning_can_also_drop_the_messages_and_the_reactions():
    client = FakeClient()

    await pyrogram.Client.ban_chat_member(
        client, -7, 9, revoke_messages=True, revoke_reactions=True
    )

    kinds = [type(q) for q in client.sent]

    assert raw.functions.channels.DeleteParticipantHistory in kinds
    assert raw.functions.messages.DeleteParticipantReactions in kinds


@pytest.mark.asyncio
async def test_a_chat_without_force_full_asks_for_the_short_one(monkeypatch):
    client = FakeClient([raw.types.messages.Chats(chats=[raw.types.ChatEmpty(id=7)])])
    client.INVITE_LINK_RE = pyrogram.Client.INVITE_LINK_RE

    def parse_chat(client, chat):
        return "short"

    monkeypatch.setattr(types.Chat, "_parse_chat", parse_chat)

    assert await pyrogram.Client.get_chat(client, -7, force_full=False) == "short"
    assert isinstance(client.sent[0], raw.functions.channels.GetChannels)


@pytest.mark.asyncio
async def test_an_emoji_status_for_a_channel_goes_to_the_channel_request():
    client = FakeClient([True])

    await pyrogram.Client.set_emoji_status(client, chat_id=-7)

    assert isinstance(client.sent[0], raw.functions.channels.UpdateEmojiStatus)

    client = FakeClient([True])

    await pyrogram.Client.set_emoji_status(client)

    assert isinstance(client.sent[0], raw.functions.account.UpdateEmojiStatus)


@pytest.mark.asyncio
async def test_a_recaptcha_token_wraps_the_query(monkeypatch):
    class Session:
        def __init__(self):
            self.query = None

        async def invoke(self, query, *args, **kwargs):
            self.query = query

            return raw.types.Updates(updates=[], users=[], chats=[], date=0, seq=0)

    client = pyrogram.Client("t", in_memory=True, api_id=1, api_hash="x")
    client.is_connected = True
    client.session = Session()
    client.rate_limiter = None

    await pyrogram.Client.invoke(
        client, raw.functions.help.GetConfig(), recaptcha_token="tok"
    )

    assert isinstance(client.session.query, raw.functions.InvokeWithReCaptcha)
    assert client.session.query.token == "tok"
