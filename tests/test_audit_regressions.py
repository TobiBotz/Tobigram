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


async def test_inviting_to_an_empty_folder_does_not_crash():
    from pyrogram import types

    class _Client:
        sent = None

        async def create_folder_invite_link(self, **kwargs):
            _Client.sent = kwargs

            return True

    folder = types.Folder(client=_Client(), id=2, name="Work")

    await folder.create_invite_link()

    assert _Client.sent["chat_ids"] == [], (
        "a folder with no included chats must send an empty chat list, not raise"
    )


async def test_a_peer_that_never_changes_is_still_written_back(tmp_path, monkeypatch):
    import time

    from pyrogram.storage import caching

    from pyrogram.storage import SQLiteStorage

    async def age(storage, peer_id, seconds):
        stale = int(time.time()) - seconds

        await storage.conn.execute("DROP TRIGGER trg_peers_last_update_on")
        await storage.conn.execute(
            "UPDATE peers SET last_update_on = ? WHERE id = ?",
            (stale, peer_id)
        )
        await storage.conn.execute(
            "CREATE TRIGGER trg_peers_last_update_on AFTER UPDATE ON peers BEGIN "
            "UPDATE peers SET last_update_on = CAST(STRFTIME('%s','now') AS INTEGER) "
            "WHERE id = NEW.id; END"
        )
        await storage._ensure_committed()

        return stale

    async def stamp_of(storage, peer_id):
        cursor = await storage.conn.execute(
            "SELECT last_update_on FROM peers WHERE id = ?", (peer_id,)
        )

        return (await cursor.fetchone())[0]

    storage = SQLiteStorage("peers", tmp_path)
    await storage.open()

    try:
        peer = (777, 123, "user", None)

        await storage.update_peers([peer])
        await storage.update_usernames([(777, ["bob"])])
        await storage._ensure_committed()

        stale = await age(storage, 777, 3600)
        await storage.update_peers([peer])
        await storage._ensure_committed()

        assert await stamp_of(storage, 777) == stale, (
            "an unchanged peer seen again within the cache window must not be rewritten"
        )

        later = time.monotonic() + storage.USERNAME_TTL
        monkeypatch.setattr(caching.time, "monotonic", lambda: later)

        await storage.update_peers([peer])
        await storage._ensure_committed()

        assert await stamp_of(storage, 777) > stale, (
            "an unchanged peer seen again after the cache window must be rewritten, "
            "or its username expires while the client is still seeing it"
        )

        await storage.get_peer_by_username("bob")

        assert storage._peer_cache.write_ttl < storage.USERNAME_TTL, (
            "a peer row must be rewritten well before the username on it expires"
        )
    finally:
        await storage.close()


async def test_a_phone_number_learned_later_is_stored(tmp_path):
    from pyrogram.storage import SQLiteStorage

    storage = SQLiteStorage("phones", tmp_path)
    await storage.open()

    try:
        await storage.update_peers([(777, 123, "user", None)])
        await storage.update_peers([(777, 123, "user", "+15551234")])
        await storage._ensure_committed()

        await storage.get_peer_by_phone_number("+15551234")
    finally:
        await storage.close()


async def test_the_obfuscated_transports_survive_their_handshake(monkeypatch):
    import asyncio

    from pyrogram.connection.transport.tcp.tcp import TCP
    from pyrogram.connection.transport.tcp.tcp_abridged_o import TCPAbridgedO
    from pyrogram.connection.transport.tcp.tcp_intermediate_o import TCPIntermediateO
    from pyrogram.connection.transport.tcp.tcp_padded_intermediate_o import (
        TCPPaddedIntermediateO,
    )
    from pyrogram.crypto import aes

    for transport_type in (TCPAbridgedO, TCPIntermediateO, TCPPaddedIntermediateO):
        wire = []

        async def connect(self, address):
            return None

        async def send(self, data, *args):
            wire.append(bytes(data))

        monkeypatch.setattr(TCP, "connect", connect)
        monkeypatch.setattr(TCP, "send", send)

        transport = transport_type(False, None, None, asyncio.get_event_loop())

        await transport.connect(("127.0.0.1", 443))

        assert len(wire) == 1 and len(wire[0]) == 64, (
            f"{transport_type.__name__} must send a 64 byte handshake nonce"
        )

        nonce = wire[0]
        peer = (bytes(nonce[8:40]), bytearray(nonce[40:56]), bytearray(1))

        aes.ctr256_decrypt(nonce, *peer)

        await transport.send(b"\x01" * 16)

        plain = aes.ctr256_decrypt(wire[1], *peer)

        assert b"\x01" * 16 in plain, (
            f"{transport_type.__name__} must encrypt its first packet with the "
            "same keystream the peer derives"
        )

        assert not isinstance(transport.encrypt[0], bytearray), (
            f"{transport_type.__name__} must hand the cipher a bytes key"
        )


async def test_the_clients_transport_choice_reaches_the_connection(monkeypatch):
    from pyrogram.connection.transport import TCPAbridgedO
    from pyrogram.session.auth import Auth
    from pyrogram.session.session import Session

    from tests.test_session import DummyClient

    seen = {}

    class _Recorded(Exception):
        pass

    def record(*args, **kwargs):
        seen.update(kwargs)

        raise _Recorded

    client = DummyClient()
    client.protocol_factory = TCPAbridgedO

    monkeypatch.setattr(client, "connection_factory", record)

    session = Session(client, 1, b"\x00" * 256, False, is_media=False, crypto_executor=None)

    with pytest.raises(_Recorded):
        await session.start(max_attempts=1)

    assert seen.get("protocol_factory") is TCPAbridgedO, (
        "Client(protocol_factory=...) must reach the connection the session opens, "
        f"got {seen.get('protocol_factory')}"
    )

    seen.clear()

    auth = Auth(client, 1, False)

    with pytest.raises(_Recorded):
        await auth.create()

    assert seen.get("protocol_factory") is TCPAbridgedO, (
        "Client(protocol_factory=...) must reach the connection that creates the "
        f"auth key, got {seen.get('protocol_factory')}"
    )


async def test_init_connection_params_reach_the_server(monkeypatch):
    from pyrogram import raw
    from pyrogram.session.session import Session

    from tests.test_session import DummyClient

    class _Connection:
        def __init__(self, *args, **kwargs):
            pass

        async def connect(self):
            pass

        async def close(self):
            pass

    sent = []

    async def send(self, query, *args, **kwargs):
        sent.append(query)

        return None

    monkeypatch.setattr(DummyClient, "connection_factory", _Connection)
    monkeypatch.setattr(Session, "send", send)
    monkeypatch.setattr(Session, "recv_worker", lambda self: asyncio.sleep(0))

    client = DummyClient()
    client.init_connection_params = {"tz_offset": 3600}

    session = Session(client, 1, b"\x00" * 256, False, is_media=False, crypto_executor=None)

    await session.start(max_attempts=1)
    await session.stop()

    init = next(
        q.query for q in sent
        if isinstance(q, raw.functions.InvokeWithLayer)
    )

    assert isinstance(init.params, raw.types.JsonObject), (
        f"init_connection_params must be sent as a JsonObject, got {init.params!r}"
    )
    assert init.params.value[0].key == "tz_offset", (
        "init_connection_params must carry the keys it was given"
    )


async def test_the_clients_connection_factory_is_the_one_that_gets_used(monkeypatch):
    import pyrogram.session.auth as auth_mod
    import pyrogram.session.session as session_mod
    from pyrogram.session.auth import Auth
    from pyrogram.session.session import Session

    from tests.test_session import DummyClient

    class _FactoryUsed(Exception):
        pass

    class _ModuleGlobalUsed(Exception):
        pass

    def chosen(*args, **kwargs):
        raise _FactoryUsed

    def ignored(*args, **kwargs):
        raise _ModuleGlobalUsed

    monkeypatch.setattr(session_mod, "Connection", ignored)
    monkeypatch.setattr(auth_mod, "Connection", ignored, raising=False)

    client = DummyClient()
    client.connection_factory = chosen

    session = Session(client, 1, b"\x00" * 256, False, is_media=False, crypto_executor=None)

    with pytest.raises(_FactoryUsed):
        await session.start(max_attempts=1)

    with pytest.raises(_FactoryUsed):
        await Auth(client, 1, False).create()


async def test_a_registered_on_connect_callback_actually_runs(monkeypatch):
    from pyrogram.session.session import Session

    from tests.test_session import DummyClient

    class _Connection:
        def __init__(self, *args, **kwargs):
            pass

        async def connect(self):
            pass

        async def close(self):
            pass

    seen = []

    async def on_connect(client, session):
        await asyncio.wait_for(session._wait_started(), timeout=2)

        seen.append((client, session))

    async def send(self, query, *args, **kwargs):
        return None

    monkeypatch.setattr(Session, "send", send)
    monkeypatch.setattr(Session, "recv_worker", lambda self: asyncio.sleep(0))

    client = DummyClient()
    client.connection_factory = _Connection
    client.connect_handler = on_connect

    session = Session(client, 1, b"\x00" * 256, False, is_media=False, crypto_executor=None)
    client.session = session

    await session.start(max_attempts=1)

    assert seen == [(client, session)], (
        "a callback registered with @on_connect must run once the session is up, "
        f"and receive (client, session); got {seen}"
    )

    await session.restart()
    await session.stop()

    assert len(seen) == 2, (
        "on_connect must run again after a reconnect, the way on_disconnect runs "
        f"again after every drop; ran {len(seen)} times"
    )


async def test_on_connect_stays_quiet_when_the_connection_never_came_up(monkeypatch):
    from pyrogram.session.session import Session

    from tests.test_session import DummyClient

    class _Refused:
        def __init__(self, *args, **kwargs):
            pass

        async def connect(self):
            raise OSError("no route to host")

        async def close(self):
            pass

    fired = []

    async def on_connect(client, session):
        fired.append(session)

    client = DummyClient()
    client.connection_factory = _Refused
    client.connect_handler = on_connect

    session = Session(client, 1, b"\x00" * 256, False, is_media=False, crypto_executor=None)
    client.session = session

    with pytest.raises(OSError):
        await session.start(max_attempts=1)

    assert not fired, (
        "on_connect must not run for a connection that never came up"
    )


async def test_the_client_counts_as_connected_while_on_connect_runs(monkeypatch):
    import pyrogram.methods.auth.connect as connect_mod
    from pyrogram.methods.auth.connect import Connect

    seen = {}

    class _Storage:
        conn = object()

        async def dc_id(self):
            return 2

        async def auth_key(self):
            return b"\x00" * 256

        async def test_mode(self):
            return False

        async def server_address(self):
            return None

        async def port(self):
            return None

        async def user_id(self):
            return 12345

    class _Session:
        fails = False

        def __init__(self, client, *args, **kwargs):
            self.client = client

        async def start(self):
            seen["is_connected"] = self.client.is_connected

            if _Session.fails:
                raise OSError("no route to host")

    class _Client(Connect):
        is_connected = False
        ipv6 = False
        crypto_executor = None
        storage = _Storage()

        async def load_session(self):
            pass

    monkeypatch.setattr(connect_mod, "Session", _Session)

    client = _Client()

    assert await client.connect() is True

    assert seen["is_connected"] is True, (
        "an on_connect callback fires from inside Session.start, so the client has "
        "to count as connected by then or client.invoke() raises ConnectionError"
    )

    _Session.fails = True
    client.is_connected = False

    with pytest.raises(OSError):
        await client.connect()

    assert client.is_connected is False, (
        "a connect that never got a session must not leave the client claiming to "
        "be connected"
    )


async def test_a_datacenter_migration_announces_the_new_connection(monkeypatch):
    import pyrogram.client as client_mod
    from pyrogram.errors import PhoneMigrate
    from pyrogram.session.session import Session

    seen = []

    class _Done(Exception):
        pass

    class _DcOption:
        ip_address = "1.2.3.4"
        port = 443

    class _Auth:
        def __init__(self, *args, **kwargs):
            pass

        async def create(self):
            return bytes(256)

    class _Connection:
        def __init__(self, *args, **kwargs):
            pass

        async def connect(self):
            pass

        async def close(self):
            pass

    async def send(self, query, *args, **kwargs):
        return None

    async def on_connect(client, session):
        seen.append(session.dc_id)

    attempts = []

    async def invoke(query, *args, **kwargs):
        attempts.append(query)

        if len(attempts) == 1:
            raise PhoneMigrate(4)

        raise _Done

    async def get_dc_option(*args, **kwargs):
        return _DcOption()

    monkeypatch.setattr(client_mod, "Auth", _Auth)
    monkeypatch.setattr(Session, "send", send)
    monkeypatch.setattr(Session, "recv_worker", lambda self: asyncio.sleep(0))

    client = pyrogram.Client("migration", api_id=1, api_hash="x", in_memory=True)
    await client.storage.open()

    try:
        await client.storage.dc_id(2)

        client.connection_factory = _Connection
        client.connect_handler = on_connect
        client.session = Session(client, 2, bytes(256), False, crypto_executor=None)

        monkeypatch.setattr(client, "invoke", invoke)
        monkeypatch.setattr(client, "get_dc_option", get_dc_option)

        with pytest.raises(_Done):
            await client.send_code("+10000000000")

        await client.session.stop()
    finally:
        await client.storage.close()

    assert seen == [4], (
        "a datacenter migration stops the old session and opens a new one, so "
        f"on_connect has to run for the new datacenter; got {seen}"
    )


async def test_a_saved_message_does_not_ask_for_a_direct_messages_topic():
    """Saved Messages carries ``saved_peer_id`` to name the saved dialog a message
    belongs to. A monoforum names its topic with the same field, and reports
    ``ChatType.PRIVATE`` like any user chat, so the chat type alone cannot tell the
    two apart: keying on it sends ``messages.GetSavedDialogsByID`` with a user as
    ``parent_peer``, and Telegram answers PARENT_PEER_INVALID. Only a monoforum
    sets ``is_direct_messages``.
    """

    from unittest.mock import Mock

    from pyrogram import raw, types

    asked = []

    client = Mock()
    client.me = Mock(id=7, is_bot=False, is_premium=False)
    client.message_cache = {}
    client.topic_cache = pyrogram.client.Cache(8)
    client.parse_mode = None
    client.fetch_topics = True

    async def get_direct_messages_topics_by_id(chat_id, topic_ids):
        asked.append((chat_id, topic_ids))
        raise AssertionError("a user chat has no direct messages topic to fetch")

    client.get_direct_messages_topics_by_id = get_direct_messages_topics_by_id

    message = raw.types.Message(
        id=1,
        peer_id=raw.types.PeerUser(user_id=7),
        from_id=raw.types.PeerUser(user_id=7),
        saved_peer_id=raw.types.PeerUser(user_id=7),
        date=1700000000,
        restriction_reason=[],
        entities=[],
        message="saved",
    )

    users = {7: raw.types.User(
        id=7, first_name="U", usernames=[], restriction_reason=[], access_hash=1, is_self=True
    )}

    parsed = await types.Message._parse(client, message, users, {})

    assert not asked, (
        "Saved Messages is a plain user chat, so parsing a message in it must not "
        f"reach for a direct messages topic; asked {asked}"
    )
    assert parsed.topic is None


async def test_a_monoforum_message_still_asks_for_its_direct_messages_topic():
    """The other half of the pairing: a monoforum reports ``ChatType.PRIVATE`` like
    any user chat, so telling the two apart by ``is_direct_messages`` has to keep
    the monoforum fetching the topic it really does own.
    """

    from unittest.mock import Mock

    from pyrogram import raw, types

    asked = []

    client = Mock()
    client.me = Mock(id=7, is_bot=False, is_premium=False)
    client.message_cache = {}
    client.topic_cache = pyrogram.client.Cache(8)
    client.parse_mode = None
    client.fetch_topics = True

    async def get_direct_messages_topics_by_id(chat_id, topic_ids):
        asked.append((chat_id, topic_ids))
        return None

    client.get_direct_messages_topics_by_id = get_direct_messages_topics_by_id

    channel = raw.types.Channel(
        id=100, title="DM", photo=raw.types.ChatPhotoEmpty(), date=0, access_hash=1,
        usernames=[], restriction_reason=[], monoforum=True, broadcast=False, megagroup=False
    )

    message = raw.types.Message(
        id=1,
        peer_id=raw.types.PeerChannel(channel_id=100),
        from_id=raw.types.PeerUser(user_id=7),
        saved_peer_id=raw.types.PeerUser(user_id=42),
        date=1700000000,
        restriction_reason=[],
        entities=[],
        message="m",
    )

    users = {7: raw.types.User(
        id=7, first_name="U", usernames=[], restriction_reason=[], access_hash=1
    )}

    parsed = await types.Message._parse(client, message, users, {100: channel})

    assert parsed.chat.is_direct_messages, "a monoforum is what marks a direct messages chat"
    assert parsed.direct_messages_topic_id == 42
    assert asked == [(parsed.chat.id, 42)], (
        f"a monoforum still owns the topic its saved_peer_id names; asked {asked}"
    )


async def test_a_saved_channel_message_does_not_read_a_user_id_off_a_channel():
    """``saved_peer_id`` in Saved Messages is whoever sent the message originally,
    and that can be a channel, which carries no ``user_id`` to read.
    """

    from unittest.mock import Mock

    from pyrogram import raw, types

    client = Mock()
    client.me = Mock(id=7, is_bot=False, is_premium=False)
    client.message_cache = {}
    client.topic_cache = pyrogram.client.Cache(8)
    client.parse_mode = None
    client.fetch_topics = True

    message = raw.types.Message(
        id=1,
        peer_id=raw.types.PeerUser(user_id=7),
        from_id=raw.types.PeerUser(user_id=7),
        saved_peer_id=raw.types.PeerChannel(channel_id=555),
        date=1700000000,
        restriction_reason=[],
        entities=[],
        message="saved from a channel",
    )

    users = {7: raw.types.User(
        id=7, first_name="U", usernames=[], restriction_reason=[], access_hash=1, is_self=True
    )}

    parsed = await types.Message._parse(client, message, users, {})

    assert parsed.direct_messages_topic_id is None
    assert parsed.topic is None
