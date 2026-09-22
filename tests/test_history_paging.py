import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pyrogram
from pyrogram import raw, types, utils


class HistoryServer:
    """A messages.GetHistory that answers the way Telegram does."""

    def __init__(self, ids):
        self.ids = sorted(ids, reverse=True)
        self.requests = 0

    async def invoke(self, query, *args, **kwargs):
        self.requests += 1

        if self.requests > 50:
            raise AssertionError("get_chat_history is not making progress")

        ordered = self.ids

        if query.offset_id:
            cursor = next((i for i, id in enumerate(ordered) if id < query.offset_id), len(ordered))
        else:
            cursor = 0

        start = max(0, cursor + query.add_offset)
        window = ordered[start : start + query.limit]

        return [
            id for id in window if id > query.min_id and (not query.max_id or id < query.max_id)
        ]

    async def resolve_peer(self, peer_id):
        return raw.types.InputPeerUser(user_id=1, access_hash=0)


@pytest.fixture
def parsed(monkeypatch):
    async def parse_messages(client, messages, replies=1):
        return [types.Message(id=id) for id in messages]

    monkeypatch.setattr(utils, "parse_messages", parse_messages)


@pytest.mark.asyncio
async def test_a_reversed_history_walks_forward_and_stops(parsed):
    server = HistoryServer(range(1, 11))

    seen = [m.id async for m in pyrogram.Client.get_chat_history(server, 7, reverse=True)]

    assert seen == list(range(1, 11))


@pytest.mark.asyncio
async def test_a_plain_history_still_walks_back_and_stops(parsed):
    server = HistoryServer(range(1, 11))

    seen = [m.id async for m in pyrogram.Client.get_chat_history(server, 7)]

    assert seen == list(range(10, 0, -1))


@pytest.mark.asyncio
async def test_a_reversed_history_crosses_page_boundaries(parsed):
    server = HistoryServer(range(1, 251))

    seen = [m.id async for m in pyrogram.Client.get_chat_history(server, 7, reverse=True)]

    assert seen == list(range(1, 251))
    assert server.requests > 2


@pytest.mark.asyncio
async def test_the_boundaries_are_inclusive_both_ways(parsed):
    forward = [
        m.id
        async for m in pyrogram.Client.get_chat_history(
            HistoryServer(range(1, 11)), 7, min_id=4, max_id=7, reverse=True
        )
    ]

    backward = [
        m.id
        async for m in pyrogram.Client.get_chat_history(
            HistoryServer(range(1, 11)), 7, min_id=4, max_id=7
        )
    ]

    assert forward == [4, 5, 6, 7]
    assert backward == [7, 6, 5, 4]


@pytest.mark.asyncio
async def test_a_limit_cuts_a_reversed_walk_short(parsed):
    server = HistoryServer(range(1, 11))

    seen = [m.id async for m in pyrogram.Client.get_chat_history(server, 7, limit=4, reverse=True)]

    assert seen == [1, 2, 3, 4]
