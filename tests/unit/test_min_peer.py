from unittest.mock import AsyncMock
import pytest
from pyrogram import Client, raw, utils
from pyrogram.errors import PeerIdInvalid


def test_get_input_user():
    channel_peer = raw.types.InputPeerChannel(channel_id=123, access_hash=456)

    # InputPeerUser
    p_user = raw.types.InputPeerUser(user_id=1001, access_hash=2002)
    u = utils.get_input_user(p_user)
    assert isinstance(u, raw.types.InputUser)
    assert u.user_id == 1001
    assert u.access_hash == 2002

    # InputPeerSelf
    p_self = raw.types.InputPeerSelf()
    u_self = utils.get_input_user(p_self)
    assert isinstance(u_self, raw.types.InputUserSelf)

    # InputPeerUserFromMessage
    p_from_msg = raw.types.InputPeerUserFromMessage(peer=channel_peer, msg_id=42, user_id=1001)
    u_from_msg = utils.get_input_user(p_from_msg)
    assert isinstance(u_from_msg, raw.types.InputUserFromMessage)
    assert u_from_msg.peer == channel_peer
    assert u_from_msg.msg_id == 42
    assert u_from_msg.user_id == 1001

    # Idempotent on InputUser types
    assert utils.get_input_user(u) is u
    assert utils.get_input_user(u_from_msg) is u_from_msg
    assert utils.get_input_user(u_self) is u_self

    # Invalid type
    with pytest.raises(ValueError):
        utils.get_input_user(channel_peer)


def test_get_input_channel():
    channel_peer = raw.types.InputPeerChannel(channel_id=123, access_hash=456)

    # InputPeerChannel
    c = utils.get_input_channel(channel_peer)
    assert isinstance(c, raw.types.InputChannel)
    assert c.channel_id == 123
    assert c.access_hash == 456

    # InputPeerChannelFromMessage
    c_from_msg = raw.types.InputPeerChannelFromMessage(peer=channel_peer, msg_id=42, channel_id=789)
    res = utils.get_input_channel(c_from_msg)
    assert isinstance(res, raw.types.InputChannelFromMessage)
    assert res.peer == channel_peer
    assert res.msg_id == 42
    assert res.channel_id == 789

    # Idempotent on InputChannel types
    assert utils.get_input_channel(c) is c
    assert utils.get_input_channel(res) is res

    # Invalid type
    with pytest.raises(ValueError):
        utils.get_input_channel(raw.types.InputPeerSelf())


def test_register_min_peers_from_message():
    client = Client("test", in_memory=True)

    channel_id = 999
    chat_id = utils.get_channel_id(channel_id)
    msg_id = 100

    min_user = raw.types.User(id=2001, min=True)
    full_user = raw.types.User(id=2002, access_hash=111, min=False)
    min_chat = raw.types.Channel(
        id=3001,
        title="Test Channel",
        photo=raw.types.ChatPhotoEmpty(),
        date=1700000000,
        min=True,
        broadcast=True,
    )

    raw_msg = raw.types.Message(
        id=msg_id,
        peer_id=raw.types.PeerChannel(channel_id=channel_id),
        from_id=raw.types.PeerUser(user_id=1001),
        date=1700000000,
        message="Hello world",
    )

    client.register_min_peers_from_message(
        raw_msg,
        users={min_user.id: min_user, full_user.id: full_user},
        chats={min_chat.id: min_chat},
    )

    # Sender user registered
    assert client._min_peer_messages.get(1001) == (chat_id, msg_id)
    # Min user registered
    assert client._min_peer_messages.get(2001) == (chat_id, msg_id)
    # Full user NOT registered as min
    assert client._min_peer_messages.get(2002) is None
    # Min channel registered (both raw id and prefixed id)
    assert client._min_peer_messages.get(3001) == (chat_id, msg_id)
    assert client._min_peer_messages.get(utils.get_channel_id(3001)) == (chat_id, msg_id)


@pytest.mark.asyncio
async def test_resolve_peer_min_user():
    client = Client("test", in_memory=True)
    await client.storage.open()
    try:
        client.is_connected = True

        channel_id = 999
        chat_id = utils.get_channel_id(channel_id)
        channel_peer = raw.types.InputPeerChannel(channel_id=channel_id, access_hash=888)

        # Storage has the channel but NOT the min user
        await client.storage.update_peers([(chat_id, 888, "channel", None)])

        # Register min user
        min_user_id = 1001
        msg_id = 50
        client.register_min_peer(min_user_id, chat_id, msg_id)

        # Resolve min user
        resolved = await client.resolve_peer(min_user_id)
        assert isinstance(resolved, raw.types.InputPeerUserFromMessage)
        assert resolved.peer == channel_peer
        assert resolved.msg_id == msg_id
        assert resolved.user_id == min_user_id
    finally:
        await client.storage.close()


@pytest.mark.asyncio
async def test_resolve_peer_min_channel():
    client = Client("test", in_memory=True)
    await client.storage.open()
    try:
        client.is_connected = True

        channel_id = 999
        chat_id = utils.get_channel_id(channel_id)
        channel_peer = raw.types.InputPeerChannel(channel_id=channel_id, access_hash=888)

        # Storage has the parent channel
        await client.storage.update_peers([(chat_id, 888, "channel", None)])

        # Register min channel
        min_chan_raw = 5555
        min_chan_id = utils.get_channel_id(min_chan_raw)
        msg_id = 75
        client.register_min_peer(min_chan_id, chat_id, msg_id)

        # Resolve min channel
        resolved = await client.resolve_peer(min_chan_id)
        assert isinstance(resolved, raw.types.InputPeerChannelFromMessage)
        assert resolved.peer == channel_peer
        assert resolved.msg_id == msg_id
        assert resolved.channel_id == min_chan_raw
    finally:
        await client.storage.close()


@pytest.mark.asyncio
async def test_resolve_peer_unknown_raises_peer_id_invalid():
    client = Client("test", in_memory=True)
    await client.storage.open()
    try:
        client.is_connected = True
        client.invoke = AsyncMock(side_effect=Exception("RPC Error"))

        with pytest.raises(PeerIdInvalid):
            await client.resolve_peer(123456789)
    finally:
        await client.storage.close()


@pytest.mark.asyncio
async def test_get_users_with_min_peer():
    client = Client("test", in_memory=True)
    client.is_connected = True

    channel_peer = raw.types.InputPeerChannel(channel_id=999, access_hash=888)
    min_peer = raw.types.InputPeerUserFromMessage(peer=channel_peer, msg_id=10, user_id=1001)

    client.resolve_peer = AsyncMock(return_value=min_peer)
    client.invoke = AsyncMock(
        return_value=[raw.types.User(id=1001, first_name="Min User", min=False)]
    )

    user = await client.get_users(1001)
    assert user.id == 1001
    assert user.first_name == "Min User"

    call_arg = client.invoke.call_args[0][0]
    assert isinstance(call_arg, raw.functions.users.GetUsers)
    # Verified: id is converted to InputUserFromMessage, NOT passed as InputPeer
    assert isinstance(call_arg.id[0], raw.types.InputUserFromMessage)
    assert call_arg.id[0].user_id == 1001
    assert call_arg.id[0].msg_id == 10


@pytest.mark.asyncio
async def test_get_chat_with_min_channel():
    client = Client("test", in_memory=True)
    client.is_connected = True

    parent_peer = raw.types.InputPeerChannel(channel_id=999, access_hash=888)
    min_chan_peer = raw.types.InputPeerChannelFromMessage(
        peer=parent_peer, msg_id=20, channel_id=5555
    )

    client.resolve_peer = AsyncMock(return_value=min_chan_peer)
    client.invoke = AsyncMock(
        return_value=raw.types.messages.ChatFull(
            full_chat=raw.types.ChannelFull(
                id=5555,
                about="Min Channel",
                read_inbox_max_id=0,
                read_outbox_max_id=0,
                unread_count=0,
                chat_photo=raw.types.PhotoEmpty(id=0),
                notify_settings=raw.types.PeerNotifySettings(),
                bot_info=[],
                pts=0,
            ),
            chats=[
                raw.types.Channel(
                    id=5555,
                    title="Min Channel Title",
                    photo=raw.types.ChatPhotoEmpty(),
                    date=1700000000,
                )
            ],
            users=[],
        )
    )

    chat = await client.get_chat(-1005555)
    assert chat.id == utils.get_channel_id(5555)

    call_arg = client.invoke.call_args[0][0]
    assert isinstance(call_arg, raw.functions.channels.GetFullChannel)
    # Verified: channel is converted to InputChannelFromMessage
    assert isinstance(call_arg.channel, raw.types.InputChannelFromMessage)
    assert call_arg.channel.channel_id == 5555
    assert call_arg.channel.msg_id == 20


@pytest.mark.asyncio
async def test_handle_updates_min_channel_peer_id_invalid():
    client = Client("test_min", in_memory=True)
    client.is_connected = True
    client.dispatcher = AsyncMock()
    client.storage = AsyncMock()
    client.resolve_peer = AsyncMock(
        return_value=raw.types.InputChannel(channel_id=1234, access_hash=5678)
    )
    client.invoke = AsyncMock(side_effect=PeerIdInvalid())

    min_user = raw.types.User(id=2001, min=True)
    min_msg = raw.types.Message(
        id=1,
        peer_id=raw.types.PeerChannel(channel_id=1234),
        date=1700000000,
        message="Hello min",
    )
    update = raw.types.UpdateNewChannelMessage(
        message=min_msg,
        pts=10,
        pts_count=1,
    )
    updates = raw.types.Updates(
        updates=[update],
        users=[min_user],
        chats=[],
        date=1700000000,
        seq=0,
    )

    # Must not raise PeerIdInvalid
    await client.handle_updates(updates)
    client.dispatcher.enqueue_update.assert_awaited_once()


@pytest.mark.asyncio
async def test_run_update_catches_unhandled_exception():
    from pyrogram.session import Session

    client = Client("dummy", in_memory=True)
    session = Session(client, dc_id=2, auth_key=b"1" * 256, test_mode=False)
    session.client.handle_updates = AsyncMock(side_effect=ValueError("Boom"))

    # Must catch and not raise exception
    await session._run_update(raw.types.Updates(updates=[], users=[], chats=[], date=0, seq=0))
