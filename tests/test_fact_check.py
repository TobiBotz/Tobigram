from unittest.mock import Mock

import pytest

import pyrogram
from pyrogram import raw, types


class FakeFactCheckClient(pyrogram.Client):
    def __init__(self):
        self.sent_queries = []
        self.me = Mock(id=111, is_bot=False)
        self.message_cache = {}
        self.topic_cache = {}

    async def resolve_peer(self, peer_id):
        if isinstance(peer_id, int):
            return raw.types.InputPeerChannel(channel_id=peer_id, access_hash=123)
        return raw.types.InputPeerChannel(channel_id=999, access_hash=123)

    async def invoke(self, query, **kwargs):
        self.sent_queries.append(query)

        if isinstance(
            query, (raw.functions.messages.DeleteFactCheck, raw.functions.messages.EditFactCheck)
        ):
            raw_msg = raw.types.Message(
                id=query.msg_id,
                peer_id=raw.types.PeerChannel(channel_id=999),
                date=1700000000,
                message="Test Message",
                entities=[],
            )
            return raw.types.Updates(
                updates=[
                    raw.types.UpdateEditChannelMessage(
                        message=raw_msg,
                        pts=10,
                        pts_count=1,
                    )
                ],
                users=[],
                chats=[
                    raw.types.Channel(
                        id=999,
                        title="Channel",
                        photo=None,
                        date=1700000000,
                    )
                ],
                date=1700000000,
                seq=0,
            )

        raise NotImplementedError(f"Unhandled query {query}")


@pytest.mark.asyncio
async def test_delete_fact_check():
    app = FakeFactCheckClient()

    # Using chat_id, message_id
    msg = await app.delete_fact_check(999, 42)
    assert isinstance(msg, types.Message)
    assert msg.id == 42

    q1 = app.sent_queries[-1]
    assert isinstance(q1, raw.functions.messages.DeleteFactCheck)
    assert q1.msg_id == 42

    # Using peer, msg_id aliases
    msg2 = await app.delete_fact_check(peer=999, msg_id=55)
    assert isinstance(msg2, types.Message)
    assert msg2.id == 55

    q2 = app.sent_queries[-1]
    assert isinstance(q2, raw.functions.messages.DeleteFactCheck)
    assert q2.msg_id == 55


@pytest.mark.asyncio
async def test_message_fact_check_bound_methods():
    app = FakeFactCheckClient()
    chat = types.Chat(id=999, type=pyrogram.enums.ChatType.CHANNEL, client=app)
    msg = types.Message(id=77, chat=chat, client=app)

    # Bound delete_fact_check
    res_del = await msg.delete_fact_check()
    assert isinstance(res_del, types.Message)
    assert res_del.id == 77
    assert isinstance(app.sent_queries[-1], raw.functions.messages.DeleteFactCheck)
    assert app.sent_queries[-1].msg_id == 77

    # Bound edit_fact_check
    res_edit = await msg.edit_fact_check(
        text_with_entities=raw.types.TextWithEntities(text="Verified true", entities=[])
    )
    assert isinstance(res_edit, types.Message)
    assert res_edit.id == 77
    assert isinstance(app.sent_queries[-1], raw.functions.messages.EditFactCheck)
    assert app.sent_queries[-1].msg_id == 77
