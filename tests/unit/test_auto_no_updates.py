from unittest.mock import AsyncMock, MagicMock

import pytest

from pyrogram import raw
from pyrogram.methods.advanced.invoke import NO_UPDATES_QUERY_NAMES, Invoke


class DummyClient(Invoke):
    def __init__(self, auto_no_updates=True, no_updates=False):
        self.is_connected = True
        self.auto_no_updates = auto_no_updates
        self.no_updates = no_updates
        self.takeout_id = None
        self.rate_limiter = None
        self.sleep_threshold = 10
        self.session = MagicMock()
        self.session.invoke = AsyncMock(
            return_value=raw.types.updates.State(pts=1, qts=0, date=1, seq=1, unread_count=0)
        )

    async def fetch_peers(self, peers):
        return False


def test_no_updates_query_names_does_not_contain_updates():
    for name in NO_UPDATES_QUERY_NAMES:
        assert not name.startswith("updates."), (
            f"Found {name} in NO_UPDATES_QUERY_NAMES: updates.* methods must never be wrapped in InvokeWithoutUpdates"
        )


def test_auto_needs_updates_for_update_methods():
    client = DummyClient()

    get_state = raw.functions.updates.GetState()
    assert client._auto_needs_updates(get_state) is True

    get_diff = raw.functions.updates.GetDifference(pts=1, date=1, qts=1)
    assert client._auto_needs_updates(get_diff) is True

    get_channel_diff = raw.functions.updates.GetChannelDifference(
        channel=raw.types.InputChannelEmpty(),
        filter=raw.types.ChannelMessagesFilterEmpty(),
        pts=1,
        limit=1,
    )
    assert client._auto_needs_updates(get_channel_diff) is True


def test_auto_needs_updates_for_read_only_methods():
    client = DummyClient()

    get_history = raw.functions.messages.GetHistory(
        peer=raw.types.InputPeerEmpty(),
        offset_id=0,
        offset_date=0,
        add_offset=0,
        limit=10,
        max_id=0,
        min_id=0,
        hash=0,
    )
    assert client._auto_needs_updates(get_history) is False

    get_users = raw.functions.users.GetUsers(id=[raw.types.InputUserEmpty()])
    assert client._auto_needs_updates(get_users) is False


@pytest.mark.asyncio
async def test_invoke_get_state_not_wrapped_in_invoke_without_updates():
    client = DummyClient(auto_no_updates=True, no_updates=False)

    get_state = raw.functions.updates.GetState()
    await client.invoke(get_state)

    called_query = client.session.invoke.call_args[0][0]
    assert isinstance(called_query, raw.functions.updates.GetState)
    assert not isinstance(called_query, raw.functions.InvokeWithoutUpdates)


@pytest.mark.asyncio
async def test_invoke_get_history_is_wrapped_when_auto_no_updates():
    client = DummyClient(auto_no_updates=True, no_updates=False)

    get_history = raw.functions.messages.GetHistory(
        peer=raw.types.InputPeerEmpty(),
        offset_id=0,
        offset_date=0,
        add_offset=0,
        limit=10,
        max_id=0,
        min_id=0,
        hash=0,
    )
    await client.invoke(get_history)

    called_query = client.session.invoke.call_args[0][0]
    assert isinstance(called_query, raw.functions.InvokeWithoutUpdates)
    assert isinstance(called_query.query, raw.functions.messages.GetHistory)


@pytest.mark.asyncio
async def test_invoke_no_updates_wraps_everything():
    client = DummyClient(auto_no_updates=True, no_updates=True)

    get_state = raw.functions.updates.GetState()
    await client.invoke(get_state)

    called_query = client.session.invoke.call_args[0][0]
    assert isinstance(called_query, raw.functions.InvokeWithoutUpdates)
