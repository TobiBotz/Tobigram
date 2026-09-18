from pathlib import Path
from unittest.mock import AsyncMock
import os
import pytest
from pyrogram import Client, raw, types


@pytest.mark.asyncio
async def test_get_send_as_chats_peer_unpacking():
    client = Client("test_sess", in_memory=True)
    raw_user = raw.types.User(id=111, is_self=True, first_name="Me")
    raw_channel = raw.types.Channel(id=222, title="My Channel", photo=None, date=0)

    mock_send_as = raw.types.channels.SendAsPeers(
        peers=[
            raw.types.SendAsPeer(peer=raw.types.PeerUser(user_id=111)),
            raw.types.SendAsPeer(peer=raw.types.PeerChannel(channel_id=222)),
        ],
        chats=[raw_channel],
        users=[raw_user],
    )

    client.resolve_peer = AsyncMock(
        return_value=raw.types.InputPeerChannel(channel_id=999, access_hash=0)
    )
    client.invoke = AsyncMock(return_value=mock_send_as)

    result = await client.get_send_as_chats(999)
    assert isinstance(result, types.List)
    assert len(result) == 2
    assert result[0].first_name == "Me"
    assert result[1].title == "My Channel"


def test_download_media_workdir_and_abs_resolution(tmp_path):
    custom_workdir = tmp_path / "custom_workdir"
    client = Client("test_sess", in_memory=True, workdir=str(custom_workdir))
    assert client.workdir == custom_workdir

    # Relative path resolution uses client.workdir
    rel_path = "subfolder/test.mp4"
    directory, file_name = os.path.split(rel_path)
    if not os.path.isabs(directory):
        directory = client.workdir / (directory or client.DEFAULT_DOWNLOAD_DIR)
    assert directory == custom_workdir / "subfolder"

    # Absolute path resolution preserves absolute directory
    abs_dir = tmp_path / "absolute_dir"
    abs_path = str(abs_dir / "test.mp4")
    directory, file_name = os.path.split(abs_path)
    if not os.path.isabs(directory):
        directory = client.workdir / (directory or client.DEFAULT_DOWNLOAD_DIR)
    assert Path(directory) == abs_dir


def test_user_and_chat_parse_none_safety():
    client = Client("test_sess", in_memory=True)

    # raw.types.User with usernames=None and restriction_reason=None
    raw_user = raw.types.User(id=12345, first_name="Test", usernames=None, restriction_reason=None)
    parsed_user = types.User._parse(client, raw_user)
    assert parsed_user is not None
    assert parsed_user.id == 12345
    assert parsed_user.usernames is None
    assert parsed_user.restrictions is None

    # Chat._parse_user_chat
    parsed_chat_user = types.Chat._parse_user_chat(client, raw_user)
    assert parsed_chat_user is not None
    assert parsed_chat_user.id == 12345
    assert parsed_chat_user.usernames is None
    assert parsed_chat_user.restrictions is None

    # Chat._parse_channel_chat
    raw_channel = raw.types.Channel(
        id=67890,
        title="Channel Test",
        usernames=None,
        restriction_reason=None,
        photo=None,
        date=0,
    )
    parsed_chat_channel = types.Chat._parse_channel_chat(client, raw_channel)
    assert parsed_chat_channel is not None
    assert parsed_chat_channel.id == -1000000067890
    assert parsed_chat_channel.usernames is None
    assert parsed_chat_channel.restrictions is None

    # Chat._parse_chat_chat
    raw_group = raw.types.Chat(
        id=112233,
        title="Group Test",
        photo=None,
        participants_count=1,
        date=0,
        version=1,
    )
    parsed_chat_group = types.Chat._parse_chat_chat(client, raw_group)
    assert parsed_chat_group is not None
    assert parsed_chat_group.id == -112233
    assert parsed_chat_group.usernames is None
