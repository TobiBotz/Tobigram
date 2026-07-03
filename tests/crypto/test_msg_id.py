import time

from pyrogram.session.internals import MsgId, _MsgIdGenerator


class TestMsgIdSingleton:
    def test_monotonic_increasing(self):
        ids = [MsgId() for _ in range(100)]
        for i in range(1, len(ids)):
            assert ids[i] > ids[i - 1]

    def test_time_based_component(self):
        now = int(time.time())
        mid = MsgId()
        high = mid >> 32
        assert high == now or high == now + 1


class TestMsgIdInstance:
    def test_instance_monotonic(self):
        gen = _MsgIdGenerator()
        ids = [gen() for _ in range(100)]
        for i in range(1, len(ids)):
            assert ids[i] > ids[i - 1]

    def test_instance_does_not_affect_singleton(self):
        gen = _MsgIdGenerator()
        gen()
        singleton_val = MsgId()
        assert isinstance(singleton_val, int)

    def test_multiple_instances_each_monotonic(self):
        a = _MsgIdGenerator()
        b = _MsgIdGenerator()
        for _ in range(10):
            av = a()
            bv = b()
            assert isinstance(av, int)
            assert isinstance(bv, int)
        ids_a = [a() for _ in range(5)]
        ids_b = [b() for _ in range(5)]
        for i in range(1, 5):
            assert ids_a[i] > ids_a[i - 1]
            assert ids_b[i] > ids_b[i - 1]

    def test_instance_repr(self):
        gen = _MsgIdGenerator()
        val = gen()
        assert isinstance(val, int)
        assert val > 0
