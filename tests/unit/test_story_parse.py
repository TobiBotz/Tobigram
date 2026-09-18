from unittest.mock import MagicMock
import pytest
from pyrogram import Client, raw, types


@pytest.mark.asyncio
async def test_story_item_deleted():
    client = Client("test", in_memory=True)
    users = {1: raw.types.User(id=1, first_name="Alice", usernames=[], restriction_reason=[])}
    chats = {}

    raw_deleted = raw.types.StoryItemDeleted(id=101)
    peer = raw.types.InputPeerUser(user_id=1, access_hash=0)

    parsed = await types.Story._parse(client, raw_deleted, users=users, chats=chats, peer=peer)

    assert isinstance(parsed, types.Story)
    assert parsed.id == 101
    assert parsed.deleted is True
    assert parsed.skipped is None
    assert parsed.raw is raw_deleted


@pytest.mark.asyncio
async def test_story_item_skipped():
    client = Client("test", in_memory=True)
    client.fetch_stories = False
    users = {1: raw.types.User(id=1, first_name="Alice", usernames=[], restriction_reason=[])}
    chats = {}

    raw_skipped = raw.types.StoryItemSkipped(
        id=202,
        date=1700000000,
        expire_date=1700086400,
        close_friends=True,
    )
    peer = raw.types.InputPeerUser(user_id=1, access_hash=0)

    parsed = await types.Story._parse(client, raw_skipped, users=users, chats=chats, peer=peer)

    assert isinstance(parsed, types.Story)
    assert parsed.id == 202
    assert parsed.skipped is True
    assert parsed.close_friends is True
    assert parsed.deleted is None
    assert parsed.date is not None
    assert parsed.expire_date is not None
    assert parsed.raw is raw_skipped


@pytest.mark.asyncio
async def test_message_media_story_bot():
    client = Client("test", in_memory=True)
    client.me = MagicMock(is_bot=True)
    users = {1: raw.types.User(id=1, first_name="Alice", usernames=[], restriction_reason=[])}
    chats = {}

    peer = raw.types.InputPeerUser(user_id=1, access_hash=0)
    raw_media_story = raw.types.MessageMediaStory(
        peer=raw.types.PeerUser(user_id=1),
        id=303,
    )

    parsed = await types.Story._parse(client, raw_media_story, peer=peer, users=users, chats=chats)

    assert isinstance(parsed, types.Story)
    assert parsed.id == 303
    assert parsed.from_user.id == 1
    assert parsed.raw is raw_media_story
