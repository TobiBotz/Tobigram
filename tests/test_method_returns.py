import inspect
import socket

import pytest

import pyrogram
from pyrogram import raw
from pyrogram.connection.transport.tcp.tcp import TCP

# Every one of these forwards the raw result untouched.
PASSTHROUGH = [
    ("can_bot_send_message", {"bot": 1}),
    ("create_business_chat_link", {"link": None}),
    ("delete_business_chat_link", {"slug": "s"}),
    ("update_business_away_message", {"message": None}),
    ("update_business_greeting_message", {"message": None}),
    ("update_business_intro", {"intro": None}),
    ("update_business_location", {"address": "a"}),
    ("update_business_work_hours", {"business_work_hours": None}),
    ("get_bot_info", {"bot": 1}),
    ("resolve_business_chat_link", {"slug": "s"}),
]


@pytest.fixture
def app():
    client = pyrogram.Client("returns", api_id=1, api_hash="x", in_memory=True)

    async def resolve_peer(*args, **kwargs):
        return raw.types.InputPeerSelf()

    client.resolve_peer = resolve_peer
    return client


@pytest.mark.parametrize("name,kwargs", PASSTHROUGH)
async def test_the_raw_result_reaches_the_caller(app, name, kwargs):
    sentinel = object()

    async def invoke(*args, **kwargs):
        return sentinel

    app.invoke = invoke

    assert await getattr(app, name)(**kwargs) is sentinel


async def test_retracting_a_vote_returns_a_poll_not_a_coroutine(app):
    poll = raw.types.Poll(
        id=1,
        hash=0,
        question=raw.types.TextWithEntities(text="q", entities=[]),
        answers=[
            raw.types.PollAnswer(
                text=raw.types.TextWithEntities(text="a", entities=[]), option=b"1"
            )
        ],
    )

    async def invoke(*args, **kwargs):
        return raw.types.Updates(
            updates=[
                raw.types.UpdateMessagePoll(
                    poll_id=1,
                    poll=poll,
                    results=raw.types.PollResults(results=[], total_voters=0),
                )
            ],
            users=[],
            chats=[],
            date=0,
            seq=0,
        )

    app.invoke = invoke

    result = await app.retract_vote(1, 2)

    assert not inspect.iscoroutine(result)
    assert isinstance(result, pyrogram.types.Poll)


async def test_closing_before_a_connection_exists_still_releases_the_socket():
    protocol = TCP(False, None)

    assert isinstance(protocol.socket, socket.socket)
    assert protocol.writer is None

    await protocol.close()

    assert protocol.socket.fileno() == -1
