from unittest.mock import Mock

import pytest

import pyrogram
from pyrogram import raw, types


class FakeStoriesClient(pyrogram.Client):
    def __init__(self):
        self.sent_queries = []
        self.me = Mock(id=111, is_bot=False, username="user")
        self.fetch_stories = False

    async def resolve_peer(self, peer_id):
        if peer_id == "me" or peer_id == 111:
            return raw.types.InputPeerSelf()
        if isinstance(peer_id, int):
            return raw.types.InputPeerChannel(channel_id=peer_id, access_hash=123)
        return raw.types.InputPeerChannel(channel_id=999, access_hash=123)

    async def get_chat(self, chat_id):
        return types.Chat(id=999, type=pyrogram.enums.ChatType.CHANNEL, client=self)

    async def invoke(self, query, **kwargs):
        self.sent_queries.append(query)

        if isinstance(query, raw.functions.stories.SendReaction):
            return raw.types.Updates(updates=[], users=[], chats=[], date=1700000000, seq=0)

        if isinstance(query, raw.functions.stories.ExportStoryLink):
            return raw.types.ExportedStoryLink(link=f"https://t.me/c/999/s/{query.id}")

        if isinstance(query, raw.functions.stories.CreateAlbum):
            return raw.types.StoryAlbum(
                album_id=42,
                title=query.title,
                icon_photo=None,
                icon_video=None,
            )

        if isinstance(query, raw.functions.stories.GetAlbums):
            return raw.types.stories.Albums(
                hash=0,
                albums=[
                    raw.types.StoryAlbum(
                        album_id=1,
                        title="Highlights 2025",
                        icon_photo=None,
                        icon_video=None,
                    ),
                    raw.types.StoryAlbum(
                        album_id=2,
                        title="Travel",
                        icon_photo=None,
                        icon_video=None,
                    ),
                ],
            )

        if isinstance(query, raw.functions.stories.DeleteAlbum):
            return True

        if isinstance(query, raw.functions.stories.UpdateAlbum):
            return raw.types.StoryAlbum(
                album_id=query.album_id,
                title=query.title or "Updated Title",
                icon_photo=None,
                icon_video=None,
            )

        if isinstance(query, raw.functions.stories.ReorderAlbums):
            return True

        if isinstance(query, raw.functions.stories.GetAlbumStories):
            if query.offset == 0:
                raw_item = raw.types.StoryItem(
                    id=10,
                    date=1700000000,
                    expire_date=1700086400,
                    media=raw.types.MessageMediaEmpty(),
                    privacy=[raw.types.PrivacyValueAllowAll()],
                )
                return raw.types.stories.Stories(
                    count=1,
                    stories=[raw_item],
                    chats=[],
                    users=[],
                    pinned_to_top=False,
                )
            return raw.types.stories.Stories(
                count=1,
                stories=[],
                chats=[],
                users=[],
                pinned_to_top=False,
            )

        if isinstance(query, raw.functions.channels.GetChannels):
            return raw.types.messages.Chats(
                chats=[
                    raw.types.Channel(
                        id=999,
                        title="Channel",
                        photo=None,
                        date=1700000000,
                    )
                ]
            )

        raise NotImplementedError(f"Unhandled query {query}")


@pytest.mark.asyncio
async def test_send_story_reaction():
    app = FakeStoriesClient()

    # With emoji str
    res1 = await app.send_story_reaction(999, 10, "❤️", add_to_recent=True)
    assert res1 is True
    q1 = app.sent_queries[-1]
    assert isinstance(q1, raw.functions.stories.SendReaction)
    assert q1.story_id == 10
    assert isinstance(q1.reaction, raw.types.ReactionEmoji)
    assert q1.reaction.emoticon == "❤️"
    assert q1.add_to_recent is True

    # With custom emoji int
    res2 = await app.send_story_reaction(999, 10, 54321)
    assert res2 is True
    q2 = app.sent_queries[-1]
    assert isinstance(q2.reaction, raw.types.ReactionCustomEmoji)
    assert q2.reaction.document_id == 54321
    assert q2.add_to_recent is False

    # Retract reaction (None)
    res3 = await app.send_story_reaction(999, 10)
    assert res3 is True
    q3 = app.sent_queries[-1]
    assert isinstance(q3.reaction, raw.types.ReactionEmpty)


@pytest.mark.asyncio
async def test_export_story_link():
    app = FakeStoriesClient()
    link = await app.export_story_link(999, 15)
    assert link == "https://t.me/c/999/s/15"
    q = app.sent_queries[-1]
    assert isinstance(q, raw.functions.stories.ExportStoryLink)
    assert q.id == 15


@pytest.mark.asyncio
async def test_create_and_manage_story_album():
    app = FakeStoriesClient()

    # Create album
    album = await app.create_story_album(999, "Summer 2026", [1, 2, 3])
    assert isinstance(album, types.StoryAlbum)
    assert album.id == 42
    assert album.title == "Summer 2026"
    assert album.chat.id == 999
    q_create = app.sent_queries[-1]
    assert isinstance(q_create, raw.functions.stories.CreateAlbum)
    assert q_create.title == "Summer 2026"
    assert q_create.stories == [1, 2, 3]

    # Get albums
    albums = await app.get_story_albums(999)
    assert len(albums) == 2
    assert albums[0].id == 1
    assert albums[0].title == "Highlights 2025"
    assert albums[1].id == 2
    assert albums[1].title == "Travel"

    # Update album
    updated = await app.update_story_album(
        999, album_id=1, title="New Highlights", add_stories=[4, 5], delete_stories=[1]
    )
    assert updated.id == 1
    assert updated.title == "New Highlights"
    q_up = app.sent_queries[-1]
    assert isinstance(q_up, raw.functions.stories.UpdateAlbum)
    assert q_up.title == "New Highlights"
    assert q_up.add_stories == [4, 5]
    assert q_up.delete_stories == [1]

    # Reorder albums
    reordered = await app.reorder_story_albums(999, [2, 1])
    assert reordered is True
    q_re = app.sent_queries[-1]
    assert isinstance(q_re, raw.functions.stories.ReorderAlbums)
    assert q_re.order == [2, 1]

    # Delete album
    deleted = await app.delete_story_album(999, 1)
    assert deleted is True
    q_del = app.sent_queries[-1]
    assert isinstance(q_del, raw.functions.stories.DeleteAlbum)
    assert q_del.album_id == 1


@pytest.mark.asyncio
async def test_get_story_album_stories():
    app = FakeStoriesClient()
    stories = []
    async for s in app.get_story_album_stories(999, 42, limit=5):
        stories.append(s)

    assert len(stories) == 1
    assert stories[0].id == 10
    q = app.sent_queries[0]
    assert isinstance(q, raw.functions.stories.GetAlbumStories)
    assert q.album_id == 42


@pytest.mark.asyncio
async def test_story_album_bound_methods():
    app = FakeStoriesClient()
    chat = types.Chat(id=999, type=pyrogram.enums.ChatType.CHANNEL, client=app)
    album = types.StoryAlbum(client=app, id=77, title="My Album", chat=chat)

    # Bound delete
    del_res = await album.delete()
    assert del_res is True
    assert isinstance(app.sent_queries[-1], raw.functions.stories.DeleteAlbum)
    assert app.sent_queries[-1].album_id == 77

    # Bound update
    up_res = await album.update(title="Renamed")
    assert up_res.id == 77
    assert isinstance(app.sent_queries[-1], raw.functions.stories.UpdateAlbum)

    # Bound get_stories
    stories = []
    async for s in album.get_stories():
        stories.append(s)
    assert len(stories) == 1
    assert stories[0].id == 10


@pytest.mark.asyncio
async def test_story_bound_methods():
    app = FakeStoriesClient()
    chat = types.Chat(id=999, type=pyrogram.enums.ChatType.CHANNEL, client=app)
    story = types.Story(id=88, chat=chat, client=app)

    # Bound react
    react_res = await story.react("🔥", add_to_recent=True)
    assert react_res is True
    q_react = app.sent_queries[-1]
    assert isinstance(q_react, raw.functions.stories.SendReaction)
    assert q_react.story_id == 88
    assert q_react.add_to_recent is True

    # Bound export_link
    exported_link = await story.export_link()
    assert exported_link == "https://t.me/c/999/s/88"
    assert isinstance(app.sent_queries[-1], raw.functions.stories.ExportStoryLink)


@pytest.mark.asyncio
async def test_copy_story_album():
    app = FakeStoriesClient()

    # Mock send_story on client
    async def fake_send_story(*args, **kwargs):
        return types.Story(id=101, client=app)

    app.send_story = fake_send_story

    # Mock story download
    async def fake_download(*args, **kwargs):
        return b"fake_media"

    types.Story.download = fake_download

    # Test copy_story_album
    new_album = await app.copy_story_album(
        chat_id=999,
        from_chat_id=999,
        album_id=1,
        title="Copied Highlights",
    )
    assert new_album.id == 42
    assert isinstance(app.sent_queries[-1], raw.functions.stories.CreateAlbum)
    assert app.sent_queries[-1].title == "Copied Highlights"
    assert app.sent_queries[-1].stories == [101]

    # Test album.copy bound method
    chat = types.Chat(id=999, type=pyrogram.enums.ChatType.CHANNEL, client=app)
    album = types.StoryAlbum(client=app, id=1, title="Original Highlights", chat=chat)

    bound_copied = await album.copy(chat_id=999)
    assert bound_copied.id == 42
