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


async def test_restricting_a_member_sends_the_granular_permissions():
    import logging

    from pyrogram import raw
    from pyrogram.methods.chats.restrict_chat_member import RestrictChatMember
    from pyrogram.methods.chats.set_chat_permissions import SetChatPermissions
    from pyrogram.types import ChatPermissions

    class _Client(RestrictChatMember, SetChatPermissions):
        sent = None

        async def resolve_peer(self, chat_id):
            return raw.types.InputPeerSelf()

        async def invoke(self, query):
            self.sent = query

            return raw.types.messages.ChatFull(
                full_chat=None, chats=[None], users=[]
            )

    async def rights_of(call, permissions):
        client = _Client()

        try:
            await call(client, permissions)
        except AttributeError:
            pass

        return client.sent.banned_rights

    allowed = ChatPermissions(
        can_send_messages=True, can_send_photos=True, can_send_videos=True
    )

    for call, label in [
        (lambda c, p: c.restrict_chat_member(-100, 1, p), "restrict_chat_member"),
        (lambda c, p: c.set_chat_permissions(-100, p), "set_chat_permissions"),
    ]:
        rights = await rights_of(call, allowed)

        assert rights.send_photos is False, (
            f"{label} granted photos, so the ban flag must say photos are not "
            "banned; hand-rolling the rights drops every granular field"
        )
        assert rights.send_videos is False, f"{label} granted videos"
        assert rights.send_media is not True, (
            f"{label}: can_send_media_messages defaults to None, so `not None` "
            "bans all media on a call that never mentioned it"
        )
        assert rights.send_reactions is not None, (
            f"{label} must decide reactions, or a muted user keeps reacting"
        )
        assert rights.manage_topics is not None, (
            f"{label} must decide topics, or a muted user keeps managing them"
        )

    logging.disable(logging.WARNING)
    try:
        legacy = await rights_of(
            lambda c, p: c.restrict_chat_member(-100, 1, p),
            ChatPermissions(can_send_messages=True, can_send_media_messages=True),
        )
    finally:
        logging.disable(logging.NOTSET)

    assert legacy.send_media is False and legacy.send_photos is None, (
        "the deprecated can_send_media_messages still has to work on its own, "
        "without the granular flags contradicting it"
    )


async def test_lifecycle_decorators_reach_the_client():
    import pyrogram
    from pyrogram.handlers import (
        ConnectHandler, DisconnectHandler, MessageHandler, StartHandler,
        StopHandler,
    )

    fired = []

    class _Client:
        name = "lifecycle"
        workers = 1
        no_updates = True
        skip_updates = True
        rate_limiter = None
        listeners = None
        start_handler = None
        stop_handler = None
        connect_handler = None
        disconnect_handler = None

        def __init__(self):
            self.loop = asyncio.get_event_loop()
            self.dispatcher = Dispatcher(self)

        async def recover_gaps(self):
            return (0, 0)

        add_handler = pyrogram.Client.add_handler
        remove_handler = pyrogram.Client.remove_handler

    def callback(name):
        async def fire(client):
            fired.append(name)

        return fire

    client = _Client()
    slots = {
        StartHandler: "start_handler",
        StopHandler: "stop_handler",
        ConnectHandler: "connect_handler",
        DisconnectHandler: "disconnect_handler",
    }
    registered = {
        handler_type: client.add_handler(handler_type(callback(attribute)))[0]
        for handler_type, attribute in slots.items()
    }

    for handler_type, attribute in slots.items():
        assert callable(getattr(client, attribute)), (
            f"{handler_type.__name__} is a lifecycle callback, so add_handler "
            "must put it on the client; parking it in dispatcher group 0 means "
            "it can never match an update and never runs"
        )

    assert not client.dispatcher.groups, (
        "no lifecycle handler belongs in a dispatcher group"
    )

    await client.dispatcher.start()
    await asyncio.sleep(0.05)
    await client.dispatcher.stop()

    assert fired == ["start_handler", "stop_handler"], (
        f"the dispatcher runs both around its own lifecycle, got {fired}"
    )

    for handler in registered.values():
        client.remove_handler(handler)

    for attribute in slots.values():
        assert getattr(client, attribute) is None, (
            f"remove_handler must clear {attribute}, not leave it firing"
        )

    client.add_handler(MessageHandler(callback("message")))
    await asyncio.sleep(0.05)

    assert [type(h).__name__ for h in client.dispatcher.groups[0]] == ["MessageHandler"], (
        "an ordinary handler still belongs to the dispatcher"
    )


async def test_removing_a_handler_spares_another_callback_of_the_same_type():
    import pyrogram
    from pyrogram.handlers import StartHandler

    class _Client:
        start_handler = None
        stop_handler = None
        connect_handler = None
        disconnect_handler = None
        dispatcher = None

        add_handler = pyrogram.Client.add_handler
        remove_handler = pyrogram.Client.remove_handler

    async def mine(client):
        pass

    async def theirs(client):
        pass

    client = _Client()
    client.add_handler(StartHandler(theirs))
    installed = client.add_handler(StartHandler(mine))[0]

    client.remove_handler(StartHandler(theirs))

    assert client.start_handler is mine, (
        "matching on type alone lets unloading one plugin clear whatever "
        "on_start another plugin installed, which the loader's exclude= path "
        "does on every run"
    )

    client.remove_handler(installed)

    assert client.start_handler is None, (
        "removing the callback that is actually installed still clears it"
    )


async def test_editing_a_folder_keeps_what_was_not_passed():
    from pyrogram import raw
    from pyrogram.methods.chats.edit_folder import EditFolder

    def make_folder():
        return raw.types.DialogFilter(
            id=2,
            title=raw.types.TextWithEntities(text="Work", entities=[]),
            pinned_peers=[raw.types.InputPeerUser(user_id=1, access_hash=1)],
            include_peers=[raw.types.InputPeerUser(user_id=2, access_hash=2)],
            exclude_peers=[raw.types.InputPeerUser(user_id=3, access_hash=3)],
            contacts=True,
            exclude_muted=True,
            emoticon="\U0001f4bc"
        )

    class _Parser:
        async def parse(self, text, parse_mode):
            return {"message": text, "entities": None}

    class _Client(EditFolder):
        parser = _Parser()

        def __init__(self, folder):
            self.folder = folder
            self.sent = None

        async def resolve_peer(self, chat_id):
            return raw.types.InputPeerUser(user_id=9, access_hash=9)

        async def invoke(self, query):
            if isinstance(query, raw.functions.messages.GetDialogFilters):
                return raw.types.messages.DialogFilters(filters=[self.folder])

            self.sent = query

            return True

    client = _Client(make_folder())

    await client.edit_folder(2, excluded_chats=["spam"])

    sent = client.sent.filter

    assert sent.title.text == "Work", (
        "editing a folder without a name must not blank its title"
    )
    assert len(sent.pinned_peers) == 1, (
        "editing a folder without pinned_chats must not drop its pinned chats"
    )
    assert len(sent.include_peers) == 1, (
        "editing a folder without included_chats must not drop its included chats"
    )
    assert sent.contacts is True and sent.exclude_muted is True, (
        "editing a folder must not reset the flags that were not passed"
    )
    assert sent.emoticon == "\U0001f4bc", (
        "editing a folder without an icon must not drop its icon"
    )
    assert [p.user_id for p in sent.exclude_peers] == [9], (
        "excluded_chats must replace the excluded peers it was given"
    )

    client = _Client(make_folder())

    await client.edit_folder(2, animate_custom_emoji=None)

    assert client.sent.filter.title_noanimate is None, (
        "omitting animate_custom_emoji must not switch name animation off"
    )


async def test_editing_a_shared_folder_rejects_a_field_it_cannot_carry():
    import pytest

    from pyrogram import raw
    from pyrogram.methods.chats.edit_folder import EditFolder

    class _Parser:
        async def parse(self, text, parse_mode):
            return {"message": text, "entities": None}

    folder = raw.types.DialogFilterChatlist(
        id=3,
        title=raw.types.TextWithEntities(text="Shared", entities=[]),
        pinned_peers=[],
        include_peers=[]
    )

    class _Client(EditFolder):
        parser = _Parser()
        sent = None

        async def resolve_peer(self, chat_id):
            return raw.types.InputPeerSelf()

        async def invoke(self, query):
            if isinstance(query, raw.functions.messages.GetDialogFilters):
                return raw.types.messages.DialogFilters(filters=[folder])

            self.sent = query

            return True

    client = _Client()

    with pytest.raises(ValueError, match="excluded_chats"):
        await client.edit_folder(3, excluded_chats=["spam"])

    assert client.sent is None, (
        "an unsupported field must be rejected before the folder is written back"
    )


async def test_editing_a_folder_can_still_clear_its_color():
    from pyrogram import enums, raw
    from pyrogram.methods.chats.edit_folder import EditFolder

    class _Client(EditFolder):
        def __init__(self):
            self.folder = raw.types.DialogFilter(
                id=2,
                title=raw.types.TextWithEntities(text="Work", entities=[]),
                pinned_peers=[],
                include_peers=[],
                exclude_peers=[],
                color=3
            )
            self.sent = None

        async def resolve_peer(self, chat_id):
            return raw.types.InputPeerSelf()

        async def invoke(self, query):
            if isinstance(query, raw.functions.messages.GetDialogFilters):
                return raw.types.messages.DialogFilters(filters=[self.folder])

            self.sent = query

            return True

    client = _Client()

    await client.edit_folder(2, color=enums.FolderColor.NO_COLOR)

    assert client.sent.filter.color is None, (
        "FolderColor.NO_COLOR must clear the color, not be read as no color given"
    )

    client = _Client()

    await client.edit_folder(2, color=enums.FolderColor.RED)

    assert client.sent.filter.color == 0, (
        "FolderColor.RED carries value 0 and must not be read as no color given"
    )

    client = _Client()

    await client.edit_folder(2, name=None)

    assert client.sent.filter.color == 3, (
        "an edit that does not mention the color must leave it alone"
    )


async def test_the_folder_edit_shortcut_keeps_its_own_pinned_chats():
    from pyrogram import types

    class _Client:
        sent = None

        async def edit_folder(self, **kwargs):
            _Client.sent = kwargs

            return True

    def chat(chat_id):
        return types.Chat(id=chat_id)

    folder = types.Folder(
        client=_Client(),
        id=2,
        name="Work",
        pinned_chats=[chat(1)],
        included_chats=[chat(1), chat(2)],
        excluded_chats=[chat(3)]
    )

    await folder.edit(exclude_muted=True)

    assert _Client.sent["pinned_chats"] == [1], (
        "editing a folder must fall back to its own pinned chats, "
        "not to its included chats"
    )

    await folder.edit(name="Work")

    assert _Client.sent["pinned_chats"] == [1], (
        "editing a folder must fall back to its own pinned chats, "
        "not to its included chats"
    )
    assert _Client.sent["included_chats"] == [1, 2], (
        "editing a folder must keep its included chats"
    )
    assert _Client.sent["excluded_chats"] == [3], (
        "editing a folder must keep its excluded chats"
    )
