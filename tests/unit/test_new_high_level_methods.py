from unittest.mock import AsyncMock, MagicMock
import pytest
from pyrogram import Client, enums, raw, types


@pytest.mark.asyncio
async def test_transcribe_audio():
    client = Client("test", in_memory=True)
    client.resolve_peer = AsyncMock(return_value=raw.types.InputPeerChat(chat_id=123))
    client.invoke = AsyncMock(
        return_value=raw.types.messages.TranscribedAudio(
            transcription_id=987654321,
            text="Hello, this is a test audio.",
            pending=False,
            trial_remains_num=5,
            trial_remains_until_date=1700000000,
        )
    )

    res = await client.transcribe_audio(chat_id=123, message_id=456)

    assert isinstance(res, types.TranscribedAudio)
    assert res.transcription_id == 987654321
    assert res.text == "Hello, this is a test audio."
    assert res.pending is False
    assert res.trial_remains_num == 5
    assert res.trial_remains_until_date is not None

    call_arg = client.invoke.call_args[0][0]
    assert isinstance(call_arg, raw.functions.messages.TranscribeAudio)
    assert call_arg.msg_id == 456


@pytest.mark.asyncio
async def test_message_transcribe_bound():
    client = Client("test", in_memory=True)
    expected = types.TranscribedAudio(transcription_id=1, text="Transcribed voice")
    client.transcribe_audio = AsyncMock(return_value=expected)

    chat = types.Chat(id=-100123456, type=enums.ChatType.SUPERGROUP, client=client)
    message = types.Message(id=789, chat=chat, client=client)

    result = await message.transcribe()
    assert result is expected
    client.transcribe_audio.assert_called_once_with(chat_id=-100123456, message_id=789)


@pytest.mark.asyncio
async def test_get_message_reactions():
    client = Client("test", in_memory=True)
    client.resolve_peer = AsyncMock(
        return_value=raw.types.InputPeerChannel(channel_id=123, access_hash=456)
    )

    peer_reaction = raw.types.MessagePeerReaction(
        peer_id=raw.types.PeerUser(user_id=1001),
        date=1700000000,
        reaction=raw.types.ReactionEmoji(emoticon="🔥"),
        big=True,
    )
    user = raw.types.User(
        id=1001,
        first_name="Tester",
        usernames=[],
        restriction_reason=[],
    )

    client.invoke = AsyncMock(
        return_value=raw.types.messages.MessageReactionsList(
            count=1,
            reactions=[peer_reaction],
            chats=[],
            users=[user],
            next_offset=None,
        )
    )

    reactions = []
    async for r in client.get_message_reactions(chat_id=123, message_id=456, reaction="🔥"):
        reactions.append(r)

    assert len(reactions) == 1
    assert isinstance(reactions[0], types.MessagePeerReaction)
    assert reactions[0].user.id == 1001
    assert reactions[0].reaction.emoji == "🔥"
    assert reactions[0].big is True

    call_arg = client.invoke.call_args[0][0]
    assert isinstance(call_arg, raw.functions.messages.GetMessageReactionsList)
    assert call_arg.id == 456
    assert isinstance(call_arg.reaction, raw.types.ReactionEmoji)
    assert call_arg.reaction.emoticon == "🔥"


@pytest.mark.asyncio
async def test_message_get_reactions_bound():
    client = Client("test", in_memory=True)
    mock_gen = MagicMock()
    client.get_message_reactions = MagicMock(return_value=mock_gen)

    chat = types.Chat(id=-100123456, type=enums.ChatType.SUPERGROUP, client=client)
    message = types.Message(id=789, chat=chat, client=client)

    res = message.get_reactions(reaction="👍", limit=10)
    assert res is mock_gen
    client.get_message_reactions.assert_called_once_with(
        chat_id=-100123456,
        message_id=789,
        reaction="👍",
        limit=10,
    )


@pytest.mark.asyncio
async def test_get_message_read_participants():
    client = Client("test", in_memory=True)
    client.resolve_peer = AsyncMock(return_value=raw.types.InputPeerChat(chat_id=123))

    raw_item = raw.types.ReadParticipantDate(user_id=2002, date=1700000000)
    client.invoke = AsyncMock(return_value=[raw_item])

    readers = await client.get_message_read_participants(chat_id=123, message_id=456)

    assert len(readers) == 1
    assert isinstance(readers[0], types.ReadParticipantDate)
    assert readers[0].user_id == 2002
    assert readers[0].date is not None

    call_arg = client.invoke.call_args[0][0]
    assert isinstance(call_arg, raw.functions.messages.GetMessageReadParticipants)
    assert call_arg.msg_id == 456


@pytest.mark.asyncio
async def test_message_get_read_participants_bound():
    client = Client("test", in_memory=True)
    expected = [
        types.ReadParticipantDate(
            user_id=2002,
            date=types.ReadParticipantDate._parse(
                None, raw.types.ReadParticipantDate(user_id=2002, date=1700000000)
            ).date,
        )
    ]
    client.get_message_read_participants = AsyncMock(return_value=expected)

    chat = types.Chat(id=-100123456, type=enums.ChatType.SUPERGROUP, client=client)
    message = types.Message(id=789, chat=chat, client=client)

    result = await message.get_read_participants()
    assert result is expected
    client.get_message_read_participants.assert_called_once_with(
        chat_id=-100123456,
        message_id=789,
    )


@pytest.mark.asyncio
async def test_search_posts():
    client = Client("test", in_memory=True)
    client.resolve_peer = AsyncMock(
        return_value=raw.types.InputPeerChannel(channel_id=555, access_hash=666)
    )

    raw_msg = raw.types.Message(
        id=42,
        peer_id=raw.types.PeerChannel(channel_id=555),
        date=1700000000,
        message="Channel post content #breaking",
        entities=[],
        restriction_reason=[],
    )
    raw_channel = raw.types.Channel(
        id=555,
        title="Breaking News",
        photo=raw.types.ChatPhotoEmpty(),
        date=1700000000,
        usernames=[],
        restriction_reason=[],
    )

    client.invoke = AsyncMock(
        return_value=raw.types.messages.MessagesSlice(
            count=1,
            messages=[raw_msg],
            chats=[raw_channel],
            users=[],
            topics=[],
        )
    )

    posts = []
    async for post in client.search_posts(query="breaking", limit=1):
        posts.append(post)

    assert len(posts) == 1
    assert isinstance(posts[0], types.Message)
    assert posts[0].id == 42
    assert posts[0].text == "Channel post content #breaking"

    call_arg = client.invoke.call_args[0][0]
    assert isinstance(call_arg, raw.functions.channels.SearchPosts)
    assert call_arg.query == "breaking"

    # Test error when neither query nor hashtag passed
    with pytest.raises(ValueError):
        async for _ in client.search_posts():
            pass


@pytest.mark.asyncio
async def test_get_inactive_channels():
    client = Client("test", in_memory=True)

    raw_channel = raw.types.Channel(
        id=777,
        title="Inactive Public Channel",
        photo=raw.types.ChatPhotoEmpty(),
        date=1700000000,
        usernames=[],
        restriction_reason=[],
    )

    client.invoke = AsyncMock(
        return_value=raw.types.messages.InactiveChats(
            dates=[1700000000],
            chats=[raw_channel],
            users=[],
        )
    )

    chats = await client.get_inactive_channels()

    assert len(chats) == 1
    assert isinstance(chats[0], types.Chat)
    assert chats[0].id == -1000000000777 or chats[0].title == "Inactive Public Channel"
    assert chats[0].title == "Inactive Public Channel"

    call_arg = client.invoke.call_args[0][0]
    assert isinstance(call_arg, raw.functions.channels.GetInactiveChannels)
