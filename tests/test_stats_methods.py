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
async def test_get_broadcast_stats_dispatches_query():
    from pyrogram.methods.stats.get_broadcast_stats import GetBroadcastStats

    class _Client(_Recorder, GetBroadcastStats):
        pass

    dummy_stats = raw.types.stats.BroadcastStats(
        period=raw.types.StatsDateRangeDays(min_date=0, max_date=1),
        followers=raw.types.StatsAbsValueAndPrev(current=10, previous=5),
        views_per_post=raw.types.StatsAbsValueAndPrev(current=10, previous=5),
        shares_per_post=raw.types.StatsAbsValueAndPrev(current=10, previous=5),
        reactions_per_post=raw.types.StatsAbsValueAndPrev(current=10, previous=5),
        views_per_story=raw.types.StatsAbsValueAndPrev(current=10, previous=5),
        shares_per_story=raw.types.StatsAbsValueAndPrev(current=10, previous=5),
        reactions_per_story=raw.types.StatsAbsValueAndPrev(current=10, previous=5),
        enabled_notifications=raw.types.StatsPercentValue(part=0.5, total=1.0),
        growth_graph=raw.types.StatsGraphError(error="none"),
        followers_graph=raw.types.StatsGraphError(error="none"),
        mute_graph=raw.types.StatsGraphError(error="none"),
        top_hours_graph=raw.types.StatsGraphError(error="none"),
        interactions_graph=raw.types.StatsGraphError(error="none"),
        iv_interactions_graph=raw.types.StatsGraphError(error="none"),
        views_by_source_graph=raw.types.StatsGraphError(error="none"),
        new_followers_by_source_graph=raw.types.StatsGraphError(error="none"),
        languages_graph=raw.types.StatsGraphError(error="none"),
        reactions_by_emotion_graph=raw.types.StatsGraphError(error="none"),
        story_interactions_graph=raw.types.StatsGraphError(error="none"),
        story_reactions_by_emotion_graph=raw.types.StatsGraphError(error="none"),
        recent_posts_interactions=[],
    )
    client = _Client(result=dummy_stats)
    res = await client.get_broadcast_stats(12345, dark=True)

    assert res == dummy_stats
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.stats.GetBroadcastStats)
    assert isinstance(call.channel, raw.types.InputPeerChannel)
    assert call.channel.channel_id == 12345
    assert call.dark is True


@pytest.mark.asyncio
async def test_get_megagroup_stats_dispatches_query():
    from pyrogram.methods.stats.get_megagroup_stats import GetMegagroupStats

    class _Client(_Recorder, GetMegagroupStats):
        pass

    dummy_stats = raw.types.stats.MegagroupStats(
        period=raw.types.StatsDateRangeDays(min_date=0, max_date=1),
        members=raw.types.StatsAbsValueAndPrev(current=100, previous=50),
        messages=raw.types.StatsAbsValueAndPrev(current=100, previous=50),
        viewers=raw.types.StatsAbsValueAndPrev(current=100, previous=50),
        posters=raw.types.StatsAbsValueAndPrev(current=100, previous=50),
        growth_graph=raw.types.StatsGraphError(error="none"),
        members_graph=raw.types.StatsGraphError(error="none"),
        new_members_by_source_graph=raw.types.StatsGraphError(error="none"),
        languages_graph=raw.types.StatsGraphError(error="none"),
        messages_graph=raw.types.StatsGraphError(error="none"),
        actions_graph=raw.types.StatsGraphError(error="none"),
        top_hours_graph=raw.types.StatsGraphError(error="none"),
        weekdays_graph=raw.types.StatsGraphError(error="none"),
        top_posters=[],
        top_admins=[],
        top_inviters=[],
        users=[],
    )
    client = _Client(result=dummy_stats)
    res = await client.get_megagroup_stats(12345, dark=False)

    assert res == dummy_stats
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.stats.GetMegagroupStats)
    assert isinstance(call.channel, raw.types.InputPeerChannel)
    assert call.channel.channel_id == 12345
    assert call.dark is False


@pytest.mark.asyncio
async def test_get_message_public_forwards_dispatches_query():
    from pyrogram.methods.stats.get_message_public_forwards import GetMessagePublicForwards

    class _Client(_Recorder, GetMessagePublicForwards):
        pass

    dummy_forwards = raw.types.stats.PublicForwards(
        count=1,
        forwards=[],
        chats=[],
        users=[],
    )
    client = _Client(result=dummy_forwards)
    res = await client.get_message_public_forwards(12345, message_id=42, offset="off1", limit=20)

    assert res == dummy_forwards
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.stats.GetMessagePublicForwards)
    assert isinstance(call.channel, raw.types.InputPeerChannel)
    assert call.channel.channel_id == 12345
    assert call.msg_id == 42
    assert call.offset == "off1"
    assert call.limit == 20


@pytest.mark.asyncio
async def test_get_message_stats_dispatches_query():
    from pyrogram.methods.stats.get_message_stats import GetMessageStats

    class _Client(_Recorder, GetMessageStats):
        pass

    dummy_stats = raw.types.stats.MessageStats(
        views_graph=raw.types.StatsGraphError(error="none"),
        reactions_by_emotion_graph=raw.types.StatsGraphError(error="none"),
    )
    client = _Client(result=dummy_stats)
    res = await client.get_message_stats(12345, message_id=99, dark=True)

    assert res == dummy_stats
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.stats.GetMessageStats)
    assert isinstance(call.channel, raw.types.InputPeerChannel)
    assert call.channel.channel_id == 12345
    assert call.msg_id == 99
    assert call.dark is True


@pytest.mark.asyncio
async def test_get_story_public_forwards_dispatches_query():
    from pyrogram.methods.stats.get_story_public_forwards import GetStoryPublicForwards

    class _Client(_Recorder, GetStoryPublicForwards):
        pass

    dummy_forwards = raw.types.stats.PublicForwards(
        count=0,
        forwards=[],
        chats=[],
        users=[],
    )
    client = _Client(result=dummy_forwards)
    res = await client.get_story_public_forwards(12345, story_id=10, offset="page2", limit=5)

    assert res == dummy_forwards
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.stats.GetStoryPublicForwards)
    assert isinstance(call.peer, raw.types.InputPeerChannel)
    assert call.peer.channel_id == 12345
    assert call.id == 10
    assert call.offset == "page2"
    assert call.limit == 5


@pytest.mark.asyncio
async def test_get_story_stats_dispatches_query():
    from pyrogram.methods.stats.get_story_stats import GetStoryStats

    class _Client(_Recorder, GetStoryStats):
        pass

    dummy_stats = raw.types.stats.StoryStats(
        views_graph=raw.types.StatsGraphError(error="none"),
        reactions_by_emotion_graph=raw.types.StatsGraphError(error="none"),
    )
    client = _Client(result=dummy_stats)
    res = await client.get_story_stats(12345, story_id=12, dark=None)

    assert res == dummy_stats
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.stats.GetStoryStats)
    assert isinstance(call.peer, raw.types.InputPeerChannel)
    assert call.peer.channel_id == 12345
    assert call.id == 12
    assert call.dark is None


@pytest.mark.asyncio
async def test_load_async_graph_dispatches_query():
    from pyrogram.methods.stats.load_async_graph import LoadAsyncGraph

    class _Client(_Recorder, LoadAsyncGraph):
        pass

    dummy_graph = raw.types.StatsGraph(
        json=raw.types.DataJSON(data='{"values": [1, 2, 3]}'),
        zoom_token=None,
    )
    client = _Client(result=dummy_graph)
    res = await client.load_async_graph(token="token123", x=123456789)

    assert res == dummy_graph
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.stats.LoadAsyncGraph)
    assert call.token == "token123"
    assert call.x == 123456789


def test_client_has_stats_methods():
    assert hasattr(pyrogram.Client, "get_broadcast_stats")
    assert hasattr(pyrogram.Client, "get_megagroup_stats")
    assert hasattr(pyrogram.Client, "get_message_public_forwards")
    assert hasattr(pyrogram.Client, "get_message_stats")
    assert hasattr(pyrogram.Client, "get_story_public_forwards")
    assert hasattr(pyrogram.Client, "get_story_stats")
    assert hasattr(pyrogram.Client, "load_async_graph")
