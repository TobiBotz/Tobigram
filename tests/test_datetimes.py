import time
from datetime import datetime, timedelta, timezone

import pytest
from pyrogram import Client, raw, types, utils


class FakeClient(Client):
    def __init__(self):
        super().__init__("test_session", api_id=12345, api_hash="0123456789abcdef0123456789abcdef")
        self.invoked = []

    async def invoke(self, query, **kwargs):
        self.invoked.append(query)
        dummy_chat = raw.types.Channel(
            id=1001,
            title="Test",
            photo=raw.types.ChatPhotoEmpty(),
            date=1700000000,
            access_hash=123,
        )
        return raw.types.Updates(updates=[], users=[], chats=[dummy_chat], date=1700000000, seq=1)

    async def resolve_peer(self, peer_id):
        return raw.types.InputPeerChannel(channel_id=1001, access_hash=123)


def test_datetime_to_timestamp_none():
    assert utils.datetime_to_timestamp(None) is None


def test_datetime_to_timestamp_datetime():
    dt = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    ts = utils.datetime_to_timestamp(dt)
    assert ts == int(dt.timestamp())


def test_datetime_to_timestamp_timedelta():
    delta = timedelta(hours=2)
    before = int(time.time()) + 7200
    ts = utils.datetime_to_timestamp(delta)
    after = int(time.time()) + 7200
    assert before <= ts <= after


@pytest.mark.asyncio
async def test_send_message_with_timedelta_schedule_date():
    client = FakeClient()
    delta = timedelta(minutes=10)
    expected_ts = int(time.time()) + 600

    await client.send_message(1001, "test message", schedule_date=delta)

    assert len(client.invoked) == 1
    req = client.invoked[0]
    assert isinstance(req, raw.functions.messages.SendMessage)
    assert abs(req.schedule_date - expected_ts) <= 2


@pytest.mark.asyncio
async def test_ban_chat_member_with_timedelta_until_date():
    client = FakeClient()
    delta = timedelta(days=7)
    expected_ts = int(time.time()) + 7 * 86400

    await client.ban_chat_member(1001, 2002, until_date=delta)

    assert len(client.invoked) == 1
    req = client.invoked[0]
    assert isinstance(req, raw.functions.channels.EditBanned)
    assert abs(req.banned_rights.until_date - expected_ts) <= 2


@pytest.mark.asyncio
async def test_restrict_chat_member_with_timedelta_until_date():
    client = FakeClient()
    delta = timedelta(days=1)
    expected_ts = int(time.time()) + 86400

    await client.restrict_chat_member(
        1001, 2002, permissions=types.ChatPermissions(), until_date=delta
    )

    assert len(client.invoked) == 1
    req = client.invoked[0]
    assert isinstance(req, raw.functions.channels.EditBanned)
    assert abs(req.banned_rights.until_date - expected_ts) <= 2
