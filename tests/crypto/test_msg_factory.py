import pytest

from pyrogram.raw.core import Message, TLObject
from pyrogram.session.internals import MsgFactory


class DummyBody(TLObject):
    def __init__(self):
        self.ID = 0x12345678

    def write(self):
        return b"\x78\x56\x34\x12"


class TestMsgFactory:
    def test_factory_creates_message(self):
        factory = MsgFactory()
        body = DummyBody()
        msg = factory(body)
        assert isinstance(msg, Message)
        assert msg.body == body.write()
        assert msg.length == 4

    def test_seq_no_increases(self):
        factory = MsgFactory()
        msg1 = factory(DummyBody())
        msg2 = factory(DummyBody())
        assert msg2.seq_no > msg1.seq_no

    def test_msg_id_increases(self):
        factory = MsgFactory()
        msg1 = factory(DummyBody())
        msg2 = factory(DummyBody())
        assert msg2.msg_id > msg1.msg_id
