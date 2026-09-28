import io
from datetime import datetime, timezone
from types import FunctionType, SimpleNamespace
from unittest.mock import AsyncMock

import pytest

import pyrogram
from pyrogram import enums, errors, raw, types, utils


def _client(answer, peer=None):
    client = pyrogram.Client("audit-iv", api_id=1, api_hash="a" * 32, in_memory=True)
    client.sent = []

    async def invoke(query, *args, **kwargs):
        client.sent.append(query)
        result = answer(query) if isinstance(answer, FunctionType) else answer

        if isinstance(result, Exception):
            raise result

        return result

    async def resolve_peer(peer_id):
        return peer or raw.types.InputPeerUser(user_id=5, access_hash=6)

    client.invoke = invoke
    client.resolve_peer = resolve_peer
    return client


def _user(id):
    return raw.types.User(
        id=id, access_hash=1, first_name=f"u{id}", usernames=[], restriction_reason=[]
    )


def _full_user(pinned):
    return raw.types.users.UserFull(
        full_user=raw.types.UserFull(
            id=5,
            settings=raw.types.PeerSettings(),
            notify_settings=raw.types.PeerNotifySettings(),
            common_chats_count=0,
            pinned_msg_id=pinned,
        ),
        chats=[],
        users=[],
    )


@pytest.mark.parametrize(
    "peer", [raw.types.InputPeerUser(user_id=5, access_hash=6), raw.types.InputPeerSelf()]
)
async def test_get_messages_pinned_reads_the_pinned_id_of_a_private_chat(peer, monkeypatch):
    async def parse_messages(client, messages, replies=1):
        return [types.Message(id=i.id) for i in client.sent[-1].id]

    monkeypatch.setattr(utils, "parse_messages", parse_messages)

    def answer(query):
        if isinstance(query, raw.functions.users.GetFullUser):
            return _full_user(42)

        return raw.types.messages.Messages(messages=[], topics=[], chats=[], users=[])

    client = _client(answer, peer)
    message = await client.get_messages("me", pinned=True)

    assert message.id == 42
    assert client.sent[-1].id == [raw.types.InputMessageID(id=42)]


async def test_get_messages_pinned_reads_the_pinned_id_of_a_basic_group(monkeypatch):
    async def parse_messages(client, messages, replies=1):
        return [types.Message(id=i.id) for i in client.sent[-1].id]

    monkeypatch.setattr(utils, "parse_messages", parse_messages)

    def answer(query):
        if isinstance(query, raw.functions.messages.GetFullChat):
            return SimpleNamespace(full_chat=SimpleNamespace(pinned_msg_id=9))

        return raw.types.messages.Messages(messages=[], topics=[], chats=[], users=[])

    client = _client(answer, raw.types.InputPeerChat(chat_id=3))

    assert (await client.get_messages(-3, pinned=True)).id == 9


async def test_get_messages_pinned_is_none_when_nothing_is_pinned():
    client = _client(_full_user(None))

    assert await client.get_messages(5, pinned=True) is None
    assert len(client.sent) == 1

    channel = _client(
        errors.MessageIdsEmpty(), raw.types.InputPeerChannel(channel_id=1, access_hash=2)
    )

    assert await channel.get_messages(-1001, pinned=True) is None

    with pytest.raises(errors.MessageIdsEmpty):
        await channel.get_messages(-1001, 5)


@pytest.mark.parametrize(
    "method,args",
    [
        ("vote_poll", (1, 2, 0)),
        ("retract_vote", (1, 2)),
        ("stop_poll", (1, 2)),
    ],
)
async def test_poll_methods_resolve_recent_voters(method, args):
    poll = raw.types.Poll(
        id=7,
        question=raw.types.TextWithEntities(text="q", entities=[]),
        hash=7,
        answers=[
            raw.types.PollAnswer(
                text=raw.types.TextWithEntities(text="a", entities=[]), option=b"0"
            )
        ],
    )
    results = raw.types.PollResults(
        results=[
            raw.types.PollAnswerVoters(
                option=b"0", voters=1, recent_voters=[raw.types.PeerUser(user_id=77)]
            )
        ],
        total_voters=1,
    )
    updates = raw.types.Updates(
        updates=[raw.types.UpdateMessagePoll(poll_id=7, poll=poll, results=results)],
        users=[_user(77)],
        chats=[],
        date=0,
        seq=0,
    )
    client = _client(updates)
    client.get_messages = AsyncMock(
        return_value=SimpleNamespace(
            poll=SimpleNamespace(id="7", options=[SimpleNamespace(persistent_id="0")])
        )
    )

    result = await getattr(client, method)(*args)

    assert [c.id for c in result.options[0].recent_voters] == [77]


@pytest.mark.parametrize("ids,sent", [(5, [5]), ((5, 6), [5, 6]), ([7], [7])])
async def test_delete_scheduled_messages_takes_an_int_or_an_iterable(ids, sent):
    client = _client(
        raw.types.Updates(
            updates=[
                raw.types.UpdateDeleteScheduledMessages(
                    peer=raw.types.PeerUser(user_id=5), messages=sent
                )
            ],
            users=[],
            chats=[],
            date=0,
            seq=0,
        )
    )

    assert await client.delete_scheduled_messages("me", ids) is True
    assert client.sent[0].id == sent


async def test_a_reversed_history_starts_at_offset_date(monkeypatch):
    async def parse_messages(client, messages, replies=1):
        return []

    monkeypatch.setattr(utils, "parse_messages", parse_messages)
    client = _client(raw.types.messages.Messages(messages=[], topics=[], chats=[], users=[]))
    date = datetime(2026, 1, 1, tzinfo=timezone.utc)

    [m async for m in client.get_chat_history(1, limit=3, reverse=True, offset_date=date)]

    assert client.sent[0].offset_id == 0
    assert client.sent[0].offset_date == utils.datetime_to_timestamp(date)

    [m async for m in client.get_chat_history(1, limit=3, reverse=True)]

    assert client.sent[1].offset_id == 1


async def test_a_short_sent_message_keeps_what_telegram_sent_back():
    webpage = raw.types.WebPage(
        id=1, url="https://telegram.org/", display_url="telegram.org", hash=0
    )
    client = _client(
        raw.types.UpdateShortSentMessage(
            id=10,
            pts=1,
            pts_count=1,
            date=0,
            out=True,
            media=raw.types.MessageMediaWebPage(webpage=webpage),
            entities=[raw.types.MessageEntityUrl(offset=4, length=20)],
        )
    )
    client.me = types.User(id=99)

    m = await client.send_message(
        5, "see https://telegram.org", reply_parameters=types.ReplyParameters(message_id=3)
    )

    assert m.reply_to_message_id == 3
    assert m.from_user.id == 99
    assert [(e.type, e.offset, e.length) for e in m.entities] == [
        (enums.MessageEntityType.URL, 4, 20)
    ]
    assert m.media == enums.MessageMediaType.WEB_PAGE
    assert m.web_page.url == "https://telegram.org/"
    assert m.link_preview_options.url == "https://telegram.org/"
    assert m.chat.type == enums.ChatType.PRIVATE
    assert m.text.entities == m.entities


async def test_a_short_sent_message_in_a_basic_group_is_a_group_with_formatted_text():
    client = _client(
        raw.types.UpdateShortSentMessage(id=10, pts=1, pts_count=1, date=0, out=True, entities=[]),
        peer=raw.types.InputPeerChat(chat_id=7),
    )
    client.me = types.User(id=99)

    m = await client.send_message(-7, "**hi** there")

    assert m.chat.id == -7
    assert m.chat.type == enums.ChatType.GROUP
    assert m.text.markdown == "**hi** there"


async def test_send_poll_applies_the_parse_mode_of_formatted_text():
    client = _client(raw.types.Updates(updates=[], users=[], chats=[], date=0, seq=0))

    await client.send_poll(
        1,
        types.FormattedText(text="**Q** x", parse_mode=enums.ParseMode.MARKDOWN),
        ["a", "b"],
        type=enums.PollType.QUIZ,
        correct_option_id=0,
        explanation=types.FormattedText(text="<b>E</b> x", parse_mode=enums.ParseMode.HTML),
        description=types.FormattedText(text="__d__", parse_mode=enums.ParseMode.MARKDOWN),
    )

    query = client.sent[0]

    assert query.media.poll.question.text == "Q x"
    assert isinstance(query.media.poll.question.entities[0], raw.types.MessageEntityBold)
    assert query.media.solution == "E x"
    assert isinstance(query.media.solution_entities[0], raw.types.MessageEntityBold)
    assert query.message == "d"
    assert isinstance(query.entities[0], raw.types.MessageEntityItalic)


@pytest.mark.parametrize("has_spoilers,expected", [(None, True), (False, False)])
async def test_copy_media_group_keeps_the_source_spoiler(has_spoilers, expected, monkeypatch):
    calls = []

    def from_file_id(**kwargs):
        calls.append(kwargs)
        return raw.types.InputMediaPhoto(
            id=raw.types.InputPhoto(id=1, access_hash=1, file_reference=b"")
        )

    monkeypatch.setattr(utils, "get_input_media_from_file_id", from_file_id)
    client = _client(raw.types.Updates(updates=[], users=[], chats=[], date=0, seq=0))
    client.get_media_group = AsyncMock(
        return_value=[
            SimpleNamespace(
                photo=SimpleNamespace(file_id="x"),
                audio=None,
                document=None,
                video=None,
                caption=None,
                caption_entities=None,
                has_media_spoiler=True,
            )
        ]
    )

    await client.copy_media_group(1, 2, 3, has_spoilers=has_spoilers)

    assert calls[0]["has_spoiler"] is expected


@pytest.mark.parametrize(
    "method,args", [("forward_messages", (1, 2, [3])), ("forward_media_group", (1, 2, 3))]
)
async def test_hide_captions_also_drops_the_author(method, args):
    client = _client(raw.types.Updates(updates=[], users=[], chats=[], date=0, seq=0))
    client.get_media_group = AsyncMock(return_value=[SimpleNamespace(id=3)])

    await getattr(client, method)(*args, hide_captions=True)
    await getattr(client, method)(*args)

    forwards = [q for q in client.sent if isinstance(q, raw.functions.messages.ForwardMessages)]

    assert (forwards[0].drop_author, forwards[0].drop_media_captions) == (True, True)
    assert not forwards[1].drop_author


async def test_media_group_mime_type_follows_file_name():
    document = raw.types.Document(
        id=1,
        access_hash=2,
        file_reference=b"",
        date=0,
        mime_type="text/plain",
        size=1,
        dc_id=2,
        attributes=[],
    )
    client = _client(
        lambda q: (
            raw.types.MessageMediaDocument(document=document)
            if isinstance(q, raw.functions.messages.UploadMedia)
            else raw.types.Updates(updates=[], users=[], chats=[], date=0, seq=0)
        )
    )
    client.save_file = AsyncMock(return_value=None)

    await client.send_media_group(
        1,
        [
            types.InputMediaDocument(io.BytesIO(b"x"), file_name="one.txt"),
            types.InputMediaAudio(io.BytesIO(b"x"), file_name="h.ogg"),
            types.InputMediaVideo(io.BytesIO(b"x"), file_name="v.webm"),
        ],
    )

    uploads = [
        q.media.mime_type for q in client.sent if isinstance(q, raw.functions.messages.UploadMedia)
    ]

    assert uploads == ["text/plain", "audio/ogg", "video/webm"]
