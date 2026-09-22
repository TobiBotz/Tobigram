import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pyrogram
from pyrogram import enums, raw, types


class FakeClient:
    def __init__(self, answers=None):
        self.sent = []
        self.answers = list(answers or [])

    async def invoke(self, query, *args, **kwargs):
        self.sent.append(query)

        if self.answers:
            return self.answers.pop(0)

        return None

    async def resolve_peer(self, peer_id):
        return raw.types.InputPeerUser(user_id=peer_id, access_hash=0)

    def rnd_id(self):
        return 1


def posts(count=None, messages=()):
    if count is None:
        return raw.types.messages.Messages(messages=list(messages), chats=[], users=[], topics=[])

    return raw.types.messages.MessagesSlice(
        count=count, messages=list(messages), chats=[], users=[], topics=[]
    )


@pytest.mark.asyncio
async def test_a_paid_reaction_carries_the_star_count():
    client = FakeClient()

    assert await pyrogram.Client.send_paid_reaction(client, 7, 11, 5) is True

    query = client.sent[0]

    assert isinstance(query, raw.functions.messages.SendPaidReaction)
    assert (query.msg_id, query.count) == (11, 5)
    assert query.private is None


@pytest.mark.asyncio
async def test_an_anonymous_paid_reaction_says_so():
    client = FakeClient()

    await pyrogram.Client.send_paid_reaction(
        client, 7, 11, 1, privacy=enums.PaidReactionPrivacy.ANONYMOUS
    )

    assert isinstance(client.sent[0].private, raw.types.PaidReactionPrivacyAnonymous)


@pytest.mark.asyncio
async def test_a_paid_reaction_as_a_chat_needs_that_chat():
    client = FakeClient()

    with pytest.raises(ValueError):
        await pyrogram.Client.send_paid_reaction(
            client, 7, 11, 1, privacy=enums.PaidReactionPrivacy.CHAT
        )

    await pyrogram.Client.send_paid_reaction(
        client, 7, 11, 1, privacy=enums.PaidReactionPrivacy.CHAT, send_as=99
    )

    assert isinstance(client.sent[0].private, raw.types.PaidReactionPrivacyPeer)


@pytest.mark.asyncio
async def test_searching_posts_counts_without_fetching_them():
    client = FakeClient([posts(count=42)])

    assert await pyrogram.Client.search_posts_count(client, "#wzgram") == 42

    query = client.sent[0]

    assert isinstance(query, raw.functions.channels.SearchPosts)
    assert query.hashtag == "wzgram"
    assert query.limit == 1


@pytest.mark.asyncio
async def test_counting_posts_falls_back_to_the_messages_it_got():
    client = FakeClient([posts(messages=[])])

    assert await pyrogram.Client.search_posts_count(client, query="wzgram") == 0
    assert client.sent[0].query == "wzgram"


@pytest.mark.asyncio
async def test_a_post_search_needs_something_to_search_for():
    with pytest.raises(ValueError):
        await pyrogram.Client.search_posts_count(FakeClient())

    with pytest.raises(ValueError):
        async for _ in pyrogram.Client.search_posts(FakeClient()):
            pass


@pytest.mark.asyncio
async def test_a_post_search_stops_at_the_limit(monkeypatch):
    from pyrogram import utils

    made = [
        types.Message(id=i, chat=types.Chat(id=-100, type=enums.ChatType.CHANNEL))
        for i in range(1, 4)
    ]

    async def parse_messages(client, messages, replies=1):
        return made

    monkeypatch.setattr(utils, "parse_messages", parse_messages)

    client = FakeClient([posts(messages=made), posts(messages=made)])
    seen = [m async for m in pyrogram.Client.search_posts(client, "wzgram", limit=2)]

    assert [m.id for m in seen] == [1, 2]
    assert len(client.sent) == 1


@pytest.mark.asyncio
async def test_gift_colors_are_sent_as_a_collectible():
    client = FakeClient([True])

    assert await pyrogram.Client.set_upgraded_gift_colors(client, 123) is True

    query = client.sent[0]

    assert isinstance(query, raw.functions.account.UpdateColor)
    assert isinstance(query.color, raw.types.InputPeerColorCollectible)
    assert query.color.collectible_id == 123


@pytest.mark.asyncio
async def test_a_live_photo_sends_the_media_the_type_built(monkeypatch):
    built = raw.types.InputMediaEmpty()

    async def write(self, **kwargs):
        return built

    monkeypatch.setattr(types.InputMediaLivePhoto, "write", write)

    from pyrogram import utils

    async def parse_text_entities(client, text, parse_mode, entities):
        return {"message": text, "entities": None}

    monkeypatch.setattr(utils, "parse_text_entities", parse_text_entities)

    async def get_reply_to(*args, **kwargs):
        return None

    monkeypatch.setattr(utils, "get_reply_to", get_reply_to)

    client = FakeClient([raw.types.Updates(updates=[], users=[], chats=[], date=0, seq=0)])

    await pyrogram.Client.send_live_photo(client, 7, "clip.mp4", "still.jpg", caption="hi")

    query = client.sent[0]

    assert isinstance(query, raw.functions.messages.SendMedia)
    assert query.media is built
    assert query.message == "hi"
