import asyncio
from types import SimpleNamespace

import pytest

import pyrogram
from pyrogram import enums, filters
from pyrogram.dispatcher import Dispatcher
from pyrogram.errors import ListenerLimitReached, ListenerStopped, ListenerTimeout
from pyrogram.handlers import MessageHandler, RawUpdateHandler
from pyrogram.methods.listeners.listen import Listen
from pyrogram.methods.listeners.register_next_step_handler import RegisterNextStepHandler
from pyrogram.methods.listeners.stop_listening import StopListening
from pyrogram.types import Identifier, Listener, ListenerRegistry
from pyrogram.types.listeners import registry as registry_module

MESSAGE = enums.ListenerTypes.MESSAGE
CALLBACK_QUERY = enums.ListenerTypes.CALLBACK_QUERY


class FakeClient(Listen, StopListening, RegisterNextStepHandler):
    def __init__(self, workers=2, max_listeners=None, listener_timeout=None):
        self.workers = workers
        self.no_updates = False
        self.skip_updates = True
        self.rate_limiter = None
        self.start_handler = None
        self.stop_handler = None
        self.executor = None
        self.max_listeners = max_listeners
        self.listener_timeout = listener_timeout
        self.unallowed_click_alert = True
        self.unallowed_click_alert_text = "not for you"
        self.loop = asyncio.get_event_loop()
        self.listeners = ListenerRegistry(self)
        self.dispatcher = Dispatcher(self)


def message(chat_id=1, user_id=10, message_id=100, outgoing=False, scheduled=False):
    return SimpleNamespace(
        chat=SimpleNamespace(id=chat_id),
        from_user=SimpleNamespace(id=user_id),
        sender_chat=None,
        id=message_id,
        outgoing=outgoing,
        scheduled=scheduled
    )


def callback_query(chat_id=1, user_id=10, message_id=100, answers=None):
    async def answer(text=None, *args, **kwargs):
        answers.append(text)

    return SimpleNamespace(
        message=SimpleNamespace(chat=SimpleNamespace(id=chat_id), id=message_id),
        from_user=SimpleNamespace(id=user_id),
        inline_message_id=None,
        answer=answer
    )


def waiting(client, listener_type=MESSAGE, timeout=None, filters=None, **criteria):
    listener = Listener(
        listener_type=listener_type,
        identifier=Identifier(**criteria),
        filters=filters,
        future=client.loop.create_future()
    )
    client.listeners.add(listener, timeout)

    return listener, listener.future


@pytest.fixture(autouse=True)
def fresh_budget():
    registry_module._budgets.clear()
    yield
    registry_module._budgets.clear()


async def test_a_listener_receives_the_matching_message():
    client = FakeClient()
    _, future = waiting(client, chat_id=1)

    assert await client.listeners.feed(client, MESSAGE, message(chat_id=1)) is True
    assert future.result().chat.id == 1
    assert not client.listeners, "a resolved listener must not stay registered"


async def test_a_message_from_another_chat_is_left_alone():
    client = FakeClient()
    waiting(client, chat_id=1)

    assert await client.listeners.feed(client, MESSAGE, message(chat_id=2)) is False


async def test_a_user_scoped_listener_is_found_without_a_chat():
    client = FakeClient()
    _, future = waiting(client, user_id=10)

    assert await client.listeners.feed(
        client, MESSAGE, message(chat_id=999, user_id=10)
    ) is True
    assert future.done()


async def test_only_the_relevant_buckets_are_probed():
    client = FakeClient()

    for chat_id in range(200):
        waiting(client, chat_id=chat_id)

    probed = client.listeners._candidates(MESSAGE, 7, 10)

    assert len(probed) == 1, (
        "an update must probe its own bucket, not every outstanding listener"
    )


async def test_the_loser_of_a_race_still_reaches_the_handlers():
    client = FakeClient()
    gate = asyncio.Event()

    async def slow(_, __, ___):
        await gate.wait()
        return True

    _, future = waiting(client, chat_id=1, filters=filters.create(slow))

    first = asyncio.ensure_future(
        client.listeners.feed(client, MESSAGE, message(message_id=1))
    )
    second = asyncio.ensure_future(
        client.listeners.feed(client, MESSAGE, message(message_id=2))
    )

    await asyncio.sleep(0)
    gate.set()

    results = await asyncio.gather(first, second)

    assert sorted(results) == [False, True], (
        "exactly one worker may consume the update; the loser has to report "
        "False so its own update still reaches the handlers"
    )
    assert future.done()


async def test_a_sync_filter_resolves_a_listener():
    client = FakeClient()

    def plain(_, __, update):
        return update.chat.id == 1

    _, future = waiting(client, chat_id=1, filters=filters.create(plain))

    assert await client.listeners.feed(client, MESSAGE, message(chat_id=1)) is True
    assert future.done(), "a plain def filter must not be awaited directly"


async def test_a_raising_filter_does_not_swallow_the_update():
    client = FakeClient()

    async def broken(_, __, ___):
        raise RuntimeError("boom")

    waiting(client, chat_id=1, filters=filters.create(broken))

    assert await client.listeners.feed(client, MESSAGE, message(chat_id=1)) is False, (
        "a listener whose filter raised must not consume the update"
    )


async def test_a_listener_ignores_outgoing_and_scheduled_messages():
    client = FakeClient()
    waiting(client, chat_id=1)

    assert await client.listeners.feed(
        client, MESSAGE, message(chat_id=1, outgoing=True)
    ) is False
    assert await client.listeners.feed(
        client, MESSAGE, message(chat_id=1, scheduled=True)
    ) is False
    assert await client.listeners.feed(client, MESSAGE, message(chat_id=1)) is True


async def test_an_unexpected_click_is_answered_and_the_listener_kept():
    client = FakeClient()
    answers = []
    _, future = waiting(
        client, listener_type=CALLBACK_QUERY, chat_id=1, user_id=10, message_id=100
    )

    consumed = await client.listeners.feed(
        client,
        CALLBACK_QUERY,
        callback_query(chat_id=1, user_id=11, answers=answers)
    )

    assert consumed is True
    assert answers == ["not for you"]
    assert not future.done(), "the rightful owner may still click"


async def test_a_next_step_callback_runs_once():
    client = FakeClient()
    seen = []

    async def callback(_, update):
        seen.append(update)

    await client.register_next_step_handler(callback, chat_id=1)

    assert await client.listeners.feed(client, MESSAGE, message(chat_id=1)) is True
    assert await client.listeners.feed(client, MESSAGE, message(chat_id=1)) is False
    assert len(seen) == 1


async def test_removal_is_idempotent_and_returns_the_budget():
    client = FakeClient()
    listener, _ = waiting(client, chat_id=1)
    budget = client.listeners.budget
    used = budget.used

    assert client.listeners.remove(listener) is True
    assert client.listeners.remove(listener) is False, "removal must be idempotent"
    assert budget.used == used - 1, "a listener may only be refunded once"
    assert not client.listeners


async def test_a_listener_filed_under_many_chats_is_refunded_once():
    client = FakeClient()
    listener, _ = waiting(client, chat_id=[1, 2, 3])
    budget = client.listeners.budget

    client.listeners.remove(listener)

    assert budget.used == 0
    assert await client.listeners.feed(client, MESSAGE, message(chat_id=2)) is False


async def test_the_budget_is_shared_between_clients():
    one = FakeClient(max_listeners=2)
    two = FakeClient(max_listeners=2)

    waiting(one, chat_id=1)
    waiting(two, chat_id=2)

    with pytest.raises(ListenerLimitReached):
        waiting(one, chat_id=3)

    assert one.listeners.budget is two.listeners.budget, (
        "a per-client cap would let fifteen clients hold fifteen times the budget"
    )


async def test_an_expired_listener_reports_a_timeout():
    client = FakeClient()
    _, future = waiting(client, chat_id=1, timeout=0.05)

    with pytest.raises(ListenerTimeout):
        await asyncio.wait_for(future, timeout=2)

    assert not client.listeners


async def test_an_earlier_deadline_interrupts_the_reaper_sleep():
    client = FakeClient()
    waiting(client, chat_id=1, timeout=30)

    await asyncio.sleep(0)

    _, urgent = waiting(client, chat_id=2, timeout=0.05)

    with pytest.raises(ListenerTimeout):
        await asyncio.wait_for(urgent, timeout=2), (
            "a nearer deadline has to wake the reaper out of its current sleep"
        )


async def test_the_reaper_steps_over_a_cancelled_waiter(caplog):
    client = FakeClient()
    _, doomed = waiting(client, chat_id=1, timeout=0.05)
    doomed.cancel()

    _, later = waiting(client, chat_id=2, timeout=0.15)

    with caplog.at_level("ERROR"):
        with pytest.raises(ListenerTimeout):
            await asyncio.wait_for(later, timeout=2)

    assert not client.listeners._reaper.done(), "the reaper has to stay alive"
    assert "Listener reaper error" not in caplog.text, (
        "expiring a cancelled future raises InvalidStateError; the reaper only "
        "survives it by way of its catch-all, and pays a backoff for each one"
    )


async def test_a_dead_reaper_is_restarted():
    client = FakeClient()

    waiting(client, chat_id=1, timeout=30)
    await asyncio.sleep(0)

    client.listeners._reaper.cancel()

    try:
        await client.listeners._reaper
    except asyncio.CancelledError:
        pass

    _, future = waiting(client, chat_id=2, timeout=0.05)

    with pytest.raises(ListenerTimeout):
        await asyncio.wait_for(future, timeout=2)


async def test_a_resolved_listener_does_not_pin_its_update_until_the_deadline():
    client = FakeClient()
    listener, _ = waiting(client, chat_id=1, timeout=3600)

    await client.listeners.feed(client, MESSAGE, message(chat_id=1))

    assert listener.future is None, (
        "the heap entry outlives resolution, so it must not keep holding the "
        "future and the parsed update behind it"
    )
    assert client.listeners._heap, "the stale entry is expected to still be queued"


async def test_closing_stops_waiters_rather_than_timing_them_out():
    client = FakeClient()
    _, future = waiting(client, chat_id=1, timeout=None)

    await client.listeners.close()

    with pytest.raises(ListenerStopped):
        await asyncio.wait_for(future, timeout=2)

    assert not client.listeners


async def test_a_closed_registry_refuses_new_listeners():
    client = FakeClient()
    await client.listeners.close()

    with pytest.raises(ListenerStopped):
        waiting(client, chat_id=1)

    client.listeners.reopen()
    waiting(client, chat_id=1)


async def test_stop_listening_reports_what_it_stopped():
    client = FakeClient()
    _, one = waiting(client, chat_id=1, user_id=10)
    _, two = waiting(client, chat_id=1, user_id=11)
    _, other = waiting(client, chat_id=2)

    assert await client.stop_listening(chat_id=1) == 2

    with pytest.raises(ListenerStopped):
        one.result()

    with pytest.raises(ListenerStopped):
        two.result()

    assert not other.done()


async def test_listen_refuses_a_client_that_never_receives_updates():
    client = FakeClient()
    client.no_updates = True

    with pytest.raises(ListenerStopped):
        await client.listen(chat_id=1)


async def test_listen_falls_back_to_the_client_timeout():
    client = FakeClient(listener_timeout=0.05)

    with pytest.raises(ListenerTimeout):
        await asyncio.wait_for(client.listen(chat_id=1), timeout=2)

    assert not client.listeners, "a timed out listener must unregister itself"


async def test_a_cancelled_listen_gives_its_slot_back():
    client = FakeClient()
    pending = asyncio.ensure_future(client.listen(chat_id=1, timeout=None))

    await asyncio.sleep(0)
    assert len(client.listeners) == 1

    pending.cancel()

    with pytest.raises(asyncio.CancelledError):
        await pending

    assert not client.listeners
    assert client.listeners.budget.used == 0


class DummyUpdate:
    pass


def dispatcher_client(workers=2):
    client = FakeClient(workers=workers)
    dispatcher = client.dispatcher

    async def parser(update, users, chats):
        return update.parsed, MessageHandler

    dispatcher.update_parsers[DummyUpdate] = parser

    return client, dispatcher


async def drain(dispatcher, timeout=2):
    deadline = asyncio.get_event_loop().time() + timeout

    while not dispatcher.updates_queue.empty():
        if asyncio.get_event_loop().time() > deadline:
            raise AssertionError("the dispatcher never drained its queue")

        await asyncio.sleep(0.01)

    await asyncio.sleep(0.05)


async def test_a_raw_handler_still_sees_an_update_a_listener_consumed():
    client, dispatcher = dispatcher_client()
    handled = []
    raw_seen = []

    dispatcher.add_handler(MessageHandler(lambda c, m: handled.append(m)), 0)
    dispatcher.add_handler(RawUpdateHandler(lambda c, u, us, cs: raw_seen.append(u)), 0)

    await dispatcher.start()

    try:
        _, future = waiting(client, chat_id=1)

        packet = DummyUpdate()
        packet.parsed = message(chat_id=1)
        await dispatcher.enqueue_update(packet, {}, {})
        await drain(dispatcher)

        assert future.done(), "the listener should have taken the update"
        assert handled == [], "a consumed update must not reach the message handlers"
        assert raw_seen == [packet], (
            "raw update handlers are a separate contract and must still fire"
        )
    finally:
        await dispatcher.stop()


async def test_an_unconsumed_update_still_reaches_the_handlers():
    client, dispatcher = dispatcher_client()
    handled = []

    dispatcher.add_handler(MessageHandler(lambda c, m: handled.append(m)), 0)

    await dispatcher.start()

    try:
        waiting(client, chat_id=999)

        packet = DummyUpdate()
        packet.parsed = message(chat_id=1)
        await dispatcher.enqueue_update(packet, {}, {})
        await drain(dispatcher)

        assert len(handled) == 1
    finally:
        await dispatcher.stop()


async def test_conversations_inside_handlers_do_not_starve_the_worker_pool():
    workers = 2
    conversations = workers + 2
    client, dispatcher = dispatcher_client(workers=workers)
    replies = []

    async def converse(_, msg):
        answer = await client.listen(chat_id=msg.chat.id, timeout=5)
        replies.append(answer.chat.id)

    dispatcher.add_handler(MessageHandler(converse), 0)

    await dispatcher.start()

    try:
        for chat_id in range(conversations):
            packet = DummyUpdate()
            packet.parsed = message(chat_id=chat_id, message_id=1)
            await dispatcher.enqueue_update(packet, {}, {})

        for _ in range(50):
            await asyncio.sleep(0.02)

            if len(client.listeners) == conversations:
                break

        assert len(client.listeners) == conversations, (
            "every conversation should have parked; a handler callback runs "
            "inline in its worker, so the pool needs relief workers to keep "
            "dispatching while they wait"
        )

        for chat_id in range(conversations):
            packet = DummyUpdate()
            packet.parsed = message(chat_id=chat_id, message_id=2)
            await dispatcher.enqueue_update(packet, {}, {})

        for _ in range(100):
            await asyncio.sleep(0.02)

            if len(replies) == conversations:
                break

        assert sorted(replies) == list(range(conversations)), (
            "with every worker parked on a listener, nothing would be left to "
            "deliver the replies those listeners are waiting for"
        )
    finally:
        await dispatcher.stop()


async def test_relief_workers_retire_once_the_conversations_end():
    client, dispatcher = dispatcher_client(workers=2)

    async def converse(_, msg):
        await client.listen(chat_id=msg.chat.id, timeout=5)

    dispatcher.add_handler(MessageHandler(converse), 0)

    await dispatcher.start()

    try:
        for chat_id in range(3):
            packet = DummyUpdate()
            packet.parsed = message(chat_id=chat_id, message_id=1)
            await dispatcher.enqueue_update(packet, {}, {})

        for _ in range(50):
            await asyncio.sleep(0.02)

            if len(client.listeners) == 3:
                break

        assert dispatcher.relief_workers, "parked workers must be covered"

        for chat_id in range(3):
            packet = DummyUpdate()
            packet.parsed = message(chat_id=chat_id, message_id=2)
            await dispatcher.enqueue_update(packet, {}, {})

        for _ in range(100):
            await asyncio.sleep(0.02)

            if dispatcher.parked == 0:
                break

        assert dispatcher.parked == 0

        for _ in range(20):
            packet = DummyUpdate()
            packet.parsed = message(chat_id=50, message_id=3)
            await dispatcher.enqueue_update(packet, {}, {})
            await asyncio.sleep(0.02)

            if not [t for t in dispatcher.relief_workers if not t.done()]:
                break

        assert not [t for t in dispatcher.relief_workers if not t.done()], (
            "relief workers have to retire, or a busy bot accumulates them"
        )
    finally:
        await dispatcher.stop()


async def test_an_idle_client_pays_almost_nothing_per_update(monkeypatch):
    client, dispatcher = dispatcher_client()
    handled = []

    dispatcher.add_handler(MessageHandler(lambda c, m: handled.append(m)), 0)

    await dispatcher.start()

    try:
        assert not client.listeners

        probed = []
        original = ListenerRegistry.feed

        async def watched(self, *args, **kwargs):
            probed.append(args)
            return await original(self, *args, **kwargs)

        monkeypatch.setattr(ListenerRegistry, "feed", watched)

        packet = DummyUpdate()
        packet.parsed = message(chat_id=1)
        await dispatcher.enqueue_update(packet, {}, {})
        await drain(dispatcher)

        assert probed == [], "an empty registry must not be walked at all"
        assert len(handled) == 1
    finally:
        await dispatcher.stop()
