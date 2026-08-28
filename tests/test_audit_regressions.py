import asyncio

import pytest

import pyrogram
from pyrogram.dispatcher import Dispatcher
from pyrogram.handlers import MessageHandler
from pyrogram.methods.rate_limiter import TokenBucket


class _DispatcherClient:
    name = "audit"
    workers = 3
    no_updates = False
    skip_updates = True
    start_handler = None
    stop_handler = None
    rate_limiter = None
    listeners = None

    def __init__(self):
        self.loop = asyncio.get_event_loop()

    async def recover_gaps(self):
        return (0, 0)


def make_dispatcher():
    return Dispatcher(_DispatcherClient())


async def test_a_dispatcher_cycle_does_not_grow_its_lock_list():
    dispatcher = make_dispatcher()

    await dispatcher.start()
    first = len(dispatcher.locks_list)
    await dispatcher.stop()

    await dispatcher.start()
    second = len(dispatcher.locks_list)
    await dispatcher.stop()

    assert first == dispatcher.client.workers
    assert second == first, (
        "every start appends one lock per worker; without a matching clear the "
        f"list grows on each cycle ({first} then {second}) for the life of the client"
    )
    assert not dispatcher.locks_list, (
        "a stopped dispatcher owns no workers, so it must hold no worker locks"
    )


async def test_a_handler_added_across_a_dispatcher_cycle_releases_what_it_took():
    dispatcher = make_dispatcher()

    first = asyncio.Lock()
    blocker = asyncio.Lock()
    await blocker.acquire()

    dispatcher.locks_list = [first, blocker]
    dispatcher.add_handler(MessageHandler(lambda *a: None), 0)

    await asyncio.sleep(0.05)
    assert first.locked(), "the barrier should be mid-acquire"

    dispatcher.locks_list = []
    blocker.release()
    await asyncio.sleep(0.05)

    assert not first.locked(), (
        "add_handler must release the locks it actually took; releasing whatever "
        "locks_list holds at the end leaves a worker lock held forever and the "
        "dispatcher stops delivering updates"
    )


async def test_the_token_bucket_lets_only_one_waiter_wait(monkeypatch):
    import pyrogram.methods.rate_limiter as rate_limiter

    waiters = 8
    bucket = TokenBucket(rate=20, burst=1)
    await bucket.acquire()

    # counting sleeps would be counting the platform clock: time.monotonic has a
    # 15.6ms resolution on Windows before 3.13, so a sleep can report less
    # elapsed than it took and cost a waiter an extra pass. How many waiters are
    # asleep at once is what tells the two designs apart, and it is exact.
    sleeping = 0
    peak = 0
    real_sleep = asyncio.sleep

    async def tracking_sleep(delay, *args, **kwargs):
        nonlocal sleeping, peak

        sleeping += 1
        peak = max(peak, sleeping)

        try:
            return await real_sleep(delay, *args, **kwargs)
        finally:
            sleeping -= 1

    monkeypatch.setattr(rate_limiter.asyncio, "sleep", tracking_sleep)

    order = []

    async def take(i):
        await bucket.acquire()
        order.append(i)

    await asyncio.gather(*(take(i) for i in range(waiters)))

    assert peak == 1, (
        "the wait is served holding the lock, so exactly one waiter is ever "
        f"asleep; {peak} of {waiters} were, which is every waiter waking for a "
        "token all but one of them will not get"
    )
    assert order == list(range(waiters)), (
        f"admission must be first-come-first-served, got {order}"
    )


class _PoolSession:
    def __init__(self, started: bool):
        self.is_started = asyncio.Event()
        self.results = {}
        self.stopped = False

        if started:
            self.is_started.set()

    @property
    def is_restarting(self) -> bool:
        return False

    async def stop(self):
        self.stopped = True


async def test_a_dead_pooled_session_is_stopped_not_orphaned(monkeypatch):
    from tests.test_media_session_pool import FakeAuth, FakeClient, FakeSession

    monkeypatch.setattr(pyrogram.client, "Session", FakeSession)
    monkeypatch.setattr(pyrogram.client, "Auth", FakeAuth)

    client = FakeClient()
    client.loop = asyncio.get_event_loop()

    dead = _PoolSession(started=False)
    client.media_session_pools[2] = [dead]

    await client._get_media_session_pool(2, 2)
    await asyncio.sleep(0.05)

    assert dead.stopped, (
        "a session dropped from the pool is no longer reachable by the reaper, so "
        "dropping it without stopping it leaks its socket and its worker tasks"
    )


async def test_upload_shutdown_does_not_wait_on_workers_that_are_gone():
    from pyrogram.methods.advanced.save_file import _stop_workers

    queue = asyncio.Queue(2)

    async def already_finished():
        return None

    workers = [asyncio.ensure_future(already_finished()) for _ in range(2)]
    await asyncio.sleep(0.05)

    queue.put_nowait("an unsent part")
    queue.put_nowait("another unsent part")

    await asyncio.wait_for(_stop_workers(queue, workers), timeout=5)


async def test_upload_shutdown_gives_up_on_a_worker_that_never_takes_its_sentinel(monkeypatch):
    from pyrogram.methods.advanced.save_file import _stop_workers
    from pyrogram.session import Session

    monkeypatch.setattr(Session, "MEDIA_WAIT_TIMEOUT", 0.1)

    queue = asyncio.Queue(2)
    queue.put_nowait("an unsent part")
    queue.put_nowait("another unsent part")

    async def finished():
        return None

    async def stuck():
        await asyncio.sleep(3600)

    workers = [asyncio.ensure_future(finished()), asyncio.ensure_future(stuck())]
    await asyncio.sleep(0.05)

    results = await asyncio.wait_for(_stop_workers(queue, workers), timeout=5)

    assert workers[1].cancelled(), (
        "a worker that cannot be handed a sentinel must be cancelled, or the "
        "gather that follows waits for it forever"
    )
    assert isinstance(results[1], asyncio.CancelledError), (
        "asking a cancelled task for its exception re-raises instead of returning, "
        "so a cancelled worker must be read from gather"
    )


async def test_editing_a_local_video_names_the_uploaded_file():
    import io

    from pyrogram import raw, types
    from pyrogram.methods.messages.edit_message_media import resolve_input_media

    class _Parser:
        async def parse(self, text, parse_mode):
            return {"message": text, "entities": None}

    class _Client:
        parser = _Parser()
        sent = None

        async def resolve_peer(self, chat_id):
            return raw.types.InputPeerSelf()

        async def save_file(self, media, **kwargs):
            if media is None:
                return None

            return raw.types.InputFile(id=1, parts=1, name="f", md5_checksum="")

        def guess_mime_type(self, media):
            return "video/mp4"

        async def invoke(self, query):
            self.sent = query

            return raw.types.MessageMediaDocument(
                document=raw.types.Document(
                    id=1, access_hash=2, file_reference=b"", date=0,
                    mime_type="video/mp4", size=1, dc_id=1, attributes=[]
                )
            )

    async def uploaded_name(media, **kwargs):
        client = _Client()
        await resolve_input_media(client, 1, media, **kwargs)

        for attribute in client.sent.media.attributes:
            if isinstance(attribute, raw.types.DocumentAttributeFilename):
                return attribute.file_name

        raise AssertionError("the upload carried no file name at all")

    buffer = io.BytesIO(b"a video")
    buffer.name = "from_the_buffer.mp4"

    assert await uploaded_name(types.InputMediaVideo(buffer)) == "from_the_buffer.mp4", (
        "with no name given anywhere the upload falls back to the media itself"
    )

    assert await uploaded_name(
        types.InputMediaVideo(buffer, file_name="on_the_media.mp4")
    ) == "on_the_media.mp4", (
        "InputMediaVideo.file_name is documented, so it must reach the wire"
    )

    assert await uploaded_name(
        types.InputMediaVideo(buffer, file_name="on_the_media.mp4"),
        file_name="on_the_call.mp4",
    ) == "on_the_call.mp4", (
        "edit_message_media's own file_name parameter is the more specific of "
        "the two, so it wins"
    )


async def test_reacting_to_a_message_sends_the_emoji():
    from pyrogram import raw
    from pyrogram.methods.messages.send_reaction import SendReaction
    from pyrogram.types import Message

    class _Client(SendReaction):
        sent = None

        async def resolve_peer(self, chat_id):
            return raw.types.InputPeerSelf()

        async def invoke(self, query, **kwargs):
            self.sent = query

            return True

    async def reaction_of(*args, **kwargs):
        client = _Client()
        message = Message(id=7, chat=object.__new__(type("C", (), {"id": -100})))
        message._client = client

        await message.react(*args, **kwargs)

        return client.sent.reaction

    assert await reaction_of("🔥") == [raw.types.ReactionEmoji(emoticon="🔥")], (
        "react must forward its emoji; sending none is the documented way to "
        "retract, so dropping it turns every reaction into a retraction"
    )

    assert await reaction_of() is None, (
        "react() with no emoji still retracts"
    )

    assert await reaction_of(5875309033427620643) == [
        raw.types.ReactionCustomEmoji(document_id=5875309033427620643)
    ], (
        "an int is a custom emoji document id, not an emoticon string"
    )

    assert await reaction_of(["🔥", 5875309033427620643]) == [
        raw.types.ReactionEmoji(emoticon="🔥"),
        raw.types.ReactionCustomEmoji(document_id=5875309033427620643),
    ], (
        "react documents a list for reacting with several emojis at once"
    )


async def test_clicking_a_url_button_returns_its_url():
    import inspect

    from pyrogram import raw
    from pyrogram.types import (
        InlineKeyboardButton, InlineKeyboardMarkup, Message,
    )

    message = Message(
        id=7,
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("open", url="https://example.org"),
        ]]),
    )

    assert await message.click() == "https://example.org", (
        "click reaches the url branch only if the branches before it stop "
        "reading attributes the button does not have"
    )

    raw_button = raw.types.KeyboardInlineButton(
        text="confirm",
        type=raw.types.InlineButtonTypeCallback(data=b"go", requires_password=True),
    )
    button = InlineKeyboardButton.read(raw_button)

    positional = [
        name
        for name in inspect.signature(InlineKeyboardButton.__init__).parameters
    ][1:]

    assert positional[:3] == ["text", "callback_data", "url"], (
        "InlineKeyboardButton is built positionally in Pyrogram code this "
        "library has to stay a drop-in replacement for, so a new parameter "
        f"belongs at the end, never inserted: {positional}"
    )

    assert button.requires_password, (
        "the flag is on the wire, so it has to survive the read or click can "
        "never tell a password button from an ordinary one"
    )
    assert (await button.write(None)).type == raw_button.type, (
        "and it has to survive the write, or a bot cannot build one"
    )


async def test_clicking_a_password_button_forwards_the_password():
    import pytest

    from pyrogram.types import (
        InlineKeyboardButton, InlineKeyboardMarkup, Message,
    )

    class _Client:
        asked = None

        async def request_callback_answer(self, **kwargs):
            self.asked = kwargs

            return True

    message = Message(
        id=7,
        chat=object.__new__(type("C", (), {"id": -100})),
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("confirm", callback_data="go", requires_password=True),
        ]]),
    )
    message._client = _Client()

    with pytest.raises(ValueError, match="requires a password"):
        await message.click()

    await message.click(password="hunter2")

    assert message._client.asked["password"] == "hunter2", (
        "a password button always carries callback data, so the password has "
        "to be forwarded from the callback branch or it is never sent at all"
    )
