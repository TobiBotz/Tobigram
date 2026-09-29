import pytest
from unittest.mock import AsyncMock, MagicMock
from pyrogram.types import Chat


@pytest.fixture
def mock_client():
    client = MagicMock()
    client.play_audio = AsyncMock(return_value=True)
    client.play_video = AsyncMock(return_value=True)
    client.join_group_call = AsyncMock(return_value=True)
    client.leave_group_call = AsyncMock(return_value=True)
    client.pause_stream = AsyncMock(return_value=True)
    client.resume_stream = AsyncMock(return_value=True)
    client.change_call_volume = AsyncMock(return_value=True)
    client.get_group_call = AsyncMock(return_value=MagicMock())
    client.create_group_call = AsyncMock(return_value=MagicMock())
    client.discard_group_call = AsyncMock(return_value=True)
    client.edit_group_call_title = AsyncMock(return_value=True)
    client.export_group_call_invite = AsyncMock(return_value="https://t.me/call")
    client.get_group_call_stream_rtmp_url = AsyncMock(return_value=MagicMock())
    client.invite_to_group_call = AsyncMock(return_value=True)
    client.start_scheduled_group_call = AsyncMock(return_value=True)
    client.toggle_group_call_record = AsyncMock(return_value=True)
    client.edit_group_call_participant = AsyncMock(return_value=True)
    client.toggle_group_call_settings = AsyncMock(return_value=True)
    return client


@pytest.mark.asyncio
async def test_chat_play(mock_client):
    chat = Chat(id=-1001234567890, client=mock_client)
    res = await chat.play("song.mp3", volume=80, muted=True)
    assert res is True
    mock_client.play_audio.assert_awaited_once_with(
        -1001234567890, path="song.mp3", volume=80, muted=True
    )


@pytest.mark.asyncio
async def test_chat_play_video(mock_client):
    chat = Chat(id=-1001234567890, client=mock_client)
    res = await chat.play_video("video.mp4", volume=90, muted=False, video_stopped=True)
    assert res is True
    mock_client.play_video.assert_awaited_once_with(
        -1001234567890, path="video.mp4", volume=90, muted=False, video_stopped=True
    )


@pytest.mark.asyncio
async def test_chat_leave_and_pause_resume(mock_client):
    chat = Chat(id=-1001234567890, client=mock_client)
    await chat.pause_stream()
    mock_client.pause_stream.assert_awaited_once_with(-1001234567890)

    await chat.resume_stream()
    mock_client.resume_stream.assert_awaited_once_with(-1001234567890)

    await chat.leave_group_call()
    mock_client.leave_group_call.assert_awaited_once_with(-1001234567890)

    await chat.join_group_call()
    mock_client.join_group_call.assert_awaited_once_with(
        -1001234567890,
        params=None,
        join_as=None,
        muted=None,
        video_stopped=None,
        invite_hash=None,
    )


@pytest.mark.asyncio
async def test_chat_call_admin_methods(mock_client):
    chat = Chat(id=-1001234567890, client=mock_client)
    await chat.create_group_call(title="Testing Call", rtmp_stream=True)
    mock_client.create_group_call.assert_awaited_once_with(
        -1001234567890, title="Testing Call", schedule_date=None, rtmp_stream=True
    )

    await chat.get_group_call()
    mock_client.get_group_call.assert_awaited_once_with(-1001234567890)

    await chat.edit_group_call_title("New Title")
    mock_client.edit_group_call_title.assert_awaited_once_with(-1001234567890, title="New Title")

    await chat.export_group_call_invite(can_self_unmute=True)
    mock_client.export_group_call_invite.assert_awaited_once_with(
        -1001234567890, can_self_unmute=True
    )

    await chat.get_group_call_stream_rtmp_url(revoke=True)
    mock_client.get_group_call_stream_rtmp_url.assert_awaited_once_with(-1001234567890, revoke=True)

    await chat.invite_to_group_call(["user1", 12345])
    mock_client.invite_to_group_call.assert_awaited_once_with(
        -1001234567890, users=["user1", 12345]
    )

    await chat.start_scheduled_group_call()
    mock_client.start_scheduled_group_call.assert_awaited_once_with(-1001234567890)

    await chat.toggle_group_call_record(start=True, title="Rec", video=True)
    mock_client.toggle_group_call_record.assert_awaited_once_with(
        -1001234567890, start=True, title="Rec", video=True, video_portrait=None
    )

    await chat.edit_group_call_participant("user1", muted=True, volume=50)
    mock_client.edit_group_call_participant.assert_awaited_once_with(
        -1001234567890,
        participant="user1",
        muted=True,
        volume=50,
        raise_hand=None,
        video_stopped=None,
        video_paused=None,
        presentation_paused=None,
    )

    await chat.toggle_group_call_settings(join_muted=True)
    mock_client.toggle_group_call_settings.assert_awaited_once_with(
        -1001234567890, reset_invite_hash=None, join_muted=True
    )

    await chat.discard_group_call()
    mock_client.discard_group_call.assert_awaited_once_with(-1001234567890)
