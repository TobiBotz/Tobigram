import pytest

import pyrogram
from pyrogram import raw, types


class _Recorder:
    def __init__(self, result=True):
        self.calls = []
        self.result = result

    async def invoke(self, query, *args, **kwargs):
        self.calls.append(query)
        return self.result

    async def resolve_peer(self, peer_id):
        if peer_id == "me" or peer_id == 111:
            return raw.types.InputPeerSelf()
        return raw.types.InputPeerChannel(
            channel_id=int(peer_id) if isinstance(peer_id, int) else 999, access_hash=123
        )

    def rnd_id(self):
        return 42


@pytest.mark.asyncio
async def test_get_stories_views_dispatches_query():
    from pyrogram.methods.stories.get_stories_views import GetStoriesViews

    class _Client(_Recorder, GetStoriesViews):
        pass

    client = _Client(result=raw.types.stories.StoryViews(views=[], users=[]))
    res = await client.get_stories_views(123, [10, 20])

    assert isinstance(res, raw.types.stories.StoryViews)
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.stories.GetStoriesViews)
    assert call.id == [10, 20]
    assert call.peer.channel_id == 123


@pytest.mark.asyncio
async def test_get_story_reactions_list_dispatches_query():
    from pyrogram.methods.stories.get_story_reactions_list import GetStoryReactionsList

    class _Client(_Recorder, GetStoryReactionsList):
        pass

    client = _Client(
        result=raw.types.stories.StoryReactionsList(count=0, reactions=[], chats=[], users=[])
    )
    res = await client.get_story_reactions_list(123, 456, limit=50, forwards_first=True)

    assert isinstance(res, raw.types.stories.StoryReactionsList)
    call = client.calls[0]
    assert isinstance(call, raw.functions.stories.GetStoryReactionsList)
    assert call.id == 456
    assert call.limit == 50
    assert call.forwards_first is True


@pytest.mark.asyncio
async def test_get_chats_to_send_stories_parses_chats():
    from pyrogram.methods.stories.get_chats_to_send_stories import GetChatsToSendStories

    raw_chat = raw.types.Channel(
        id=999,
        title="Test Channel",
        photo=raw.types.ChatPhotoEmpty(),
        date=1700000000,
    )

    class _Client(_Recorder, GetChatsToSendStories):
        pass

    client = _Client(result=raw.types.messages.Chats(chats=[raw_chat]))
    chats = await client.get_chats_to_send_stories()

    assert len(chats) == 1
    assert isinstance(chats[0], types.Chat)
    assert chats[0].id == -1000000000999
    assert isinstance(client.calls[0], raw.functions.stories.GetChatsToSend)


@pytest.mark.asyncio
async def test_search_stories_dispatches_query():
    from pyrogram.methods.stories.search_stories import SearchStories

    class _Client(_Recorder, SearchStories):
        pass

    client = _Client(result=raw.types.stories.FoundStories(count=0, stories=[], chats=[], users=[]))
    res = await client.search_stories(hashtag="news", chat_id=123, limit=20)

    assert isinstance(res, raw.types.stories.FoundStories)
    call = client.calls[0]
    assert isinstance(call, raw.functions.stories.SearchPosts)
    assert call.hashtag == "news"
    assert call.peer.channel_id == 123
    assert call.limit == 20


@pytest.mark.asyncio
async def test_start_live_story_passes_random_id_and_peer():
    from pyrogram.methods.stories.start_live_story import StartLiveStory

    class _Client(_Recorder, StartLiveStory):
        pass

    client = _Client(result=raw.types.Updates(updates=[], users=[], chats=[], date=0, seq=0))
    await client.start_live_story(123, caption="Live test")

    call = client.calls[0]
    assert isinstance(call, raw.functions.stories.StartLive)
    assert call.caption == "Live test"
    assert call.random_id == 42
    assert call.peer.channel_id == 123


@pytest.mark.asyncio
async def test_toggle_stories_pinned_to_top_handles_single_and_list():
    from pyrogram.methods.stories.toggle_stories_pinned_to_top import ToggleStoriesPinnedToTop

    class _Client(_Recorder, ToggleStoriesPinnedToTop):
        pass

    client = _Client()
    await client.toggle_stories_pinned_to_top(123, 77)

    call = client.calls[0]
    assert isinstance(call, raw.functions.stories.TogglePinnedToTop)
    assert call.id == [77]

    await client.toggle_stories_pinned_to_top(123, [88, 99])
    assert client.calls[1].id == [88, 99]


@pytest.mark.asyncio
async def test_toggle_all_stories_hidden_dispatches_flag():
    from pyrogram.methods.stories.toggle_all_stories_hidden import ToggleAllStoriesHidden

    class _Client(_Recorder, ToggleAllStoriesHidden):
        pass

    client = _Client()
    await client.toggle_all_stories_hidden(True)
    assert client.calls[0].hidden is True

    await client.toggle_all_stories_hidden(False)
    assert client.calls[1].hidden is False


@pytest.mark.asyncio
async def test_get_all_read_peer_stories_dispatches_query():
    from pyrogram.methods.stories.get_all_read_peer_stories import GetAllReadPeerStories

    class _Client(_Recorder, GetAllReadPeerStories):
        pass

    client = _Client()
    await client.get_all_read_peer_stories()
    assert isinstance(client.calls[0], raw.functions.stories.GetAllReadPeerStories)


@pytest.mark.asyncio
async def test_get_peer_max_story_ids_resolves_all_peers():
    from pyrogram.methods.stories.get_peer_max_story_ids import GetPeerMaxStoryIDs

    class _Client(_Recorder, GetPeerMaxStoryIDs):
        pass

    client = _Client(result=[raw.types.RecentStory(max_id=45)])
    res = await client.get_peer_max_story_ids([123, 456])

    assert len(res) == 1
    assert res[0].max_id == 45
    call = client.calls[0]
    assert isinstance(call, raw.functions.stories.GetPeerMaxIDs)
    assert len(call.id) == 2
