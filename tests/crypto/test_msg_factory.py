import pytest

from pyrogram.raw.core import Message, TLObject
from pyrogram.raw.functions import Ping
from pyrogram.raw.types import MsgsAck, HttpWait
from pyrogram.session.internals import MsgFactory, _MsgIdGenerator
from pyrogram.session.internals.msg_factory import not_content_related
from pyrogram.session.internals.seq_no import SeqNo


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

    def test_not_content_related_tuple(self):
        assert Ping in not_content_related
        assert HttpWait in not_content_related
        assert MsgsAck in not_content_related

    def test_content_related_seq_no(self):
        factory = MsgFactory()
        msg = factory(DummyBody())
        assert msg.seq_no == 1  # content-related: (0 * 2) + 1

    def test_not_content_related_seq_no(self):
        factory = MsgFactory()
        msg = factory(Ping(ping_id=0))
        assert msg.seq_no == 0  # not content-related: (0 * 2) + 0

    def test_seq_no_pattern_content_then_non_content(self):
        factory = MsgFactory()
        m1 = factory(DummyBody())         # content-related -> seq_no=1
        m2 = factory(Ping(ping_id=0))      # not content-related -> seq_no=2
        m3 = factory(DummyBody())          # content-related -> seq_no=3
        assert m1.seq_no == 1
        assert m2.seq_no == 2
        assert m3.seq_no == 3

    def test_seq_no_only_content_related_increments_counter(self):
        factory = MsgFactory()
        factory(DummyBody())           # content_related_messages_sent = 1
        factory(DummyBody())           # content_related_messages_sent = 2
        factory(Ping(ping_id=0))       # not content-related
        m = factory(DummyBody())       # content-related -> seq_no = (2 * 2) + 1 = 5
        assert m.seq_no == 5

    def test_custom_msg_id_generator(self):
        gen = _MsgIdGenerator()
        id1 = gen()
        factory = MsgFactory(msg_id_generator=gen)
        m = factory(DummyBody())
        assert m.msg_id > id1

    def test_body_length_matches(self):
        class FixedBody(TLObject):
            def write(self):
                return b"\x01\x02\x03\x04\x05"
        factory = MsgFactory()
        body = FixedBody()
        msg = factory(body)
        assert msg.length == 5
        assert msg.length == len(body)

    def test_factory_accepts_ping(self):
        factory = MsgFactory()
        msg = factory(Ping(ping_id=0))
        assert isinstance(msg, Message)
        assert msg.length == len(Ping(ping_id=0))

    def test_multiple_factories_independent_seq_no(self):
        f1 = MsgFactory()
        f2 = MsgFactory()
        f1(DummyBody())
        f2(DummyBody())
        assert f1.seq_no.content_related_messages_sent == 1
        assert f2.seq_no.content_related_messages_sent == 1

    def test_multiple_factories_use_separate_generators(self):
        f1 = MsgFactory()
        gen2 = _MsgIdGenerator()
        f2 = MsgFactory(msg_id_generator=gen2)
        m1 = f1(DummyBody())
        m2 = f2(DummyBody())
        assert isinstance(m1.msg_id, int)
        assert isinstance(m2.msg_id, int)
