import asyncio
import inspect
from types import SimpleNamespace

import pytest

import pyrogram
from pyrogram import enums, filters, raw, types, utils
from pyrogram.methods.bots.check_bot_username import CheckBotUsername
from pyrogram.methods.bots.get_bot_default_privileges import GetBotDefaultPrivileges
from pyrogram.storage.caching import PeerRowCache
from pyrogram.types.listeners.registry import ListenerRegistry


def reply_keyboard_message():
    keyboard = types.ReplyKeyboardMarkup(
        [
            ["Yes", "No"],
            [
                types.KeyboardButton("Styled", style=enums.ButtonStyle.SUCCESS),
                types.KeyboardButton("Share", request_contact=True),
            ],
        ]
    )

    return types.Message(id=1, chat=types.Chat(id=5), reply_markup=keyboard)


@pytest.fixture
def sent(monkeypatch):
    calls = []

    async def send(self, text, *args, **kwargs):
        calls.append(text)
        return f"sent:{text}"

    monkeypatch.setattr(types.Message, "answer", send)
    monkeypatch.setattr(types.Message, "reply", send)

    return calls


@pytest.mark.parametrize(
    "args, expected",
    [
        ((0,), "Yes"),
        (("No",), "No"),
        (("Styled",), "Styled"),
        ((1, 1), "Share"),
        ((0, 1), "Styled"),
    ],
)
async def test_click_reply_keyboard_sends_button_text_and_returns_result(sent, args, expected):
    result = await reply_keyboard_message().click(*args)

    assert sent == [expected]
    assert result == f"sent:{expected}"


async def test_click_reply_keyboard_quote_returns_result(sent):
    result = await reply_keyboard_message().click("Share", quote=True)

    assert sent == ["Share"]
    assert result == "sent:Share"


async def test_click_copy_text_button_returns_string():
    keyboard = types.InlineKeyboardMarkup(
        [[types.InlineKeyboardButton("C", copy_text=types.CopyTextButton("copied"))]]
    )
    message = types.Message(id=1, chat=types.Chat(id=5), reply_markup=keyboard)

    assert await message.click(0) == "copied"


def deleted_channel_update_client(peer_type):
    peer_cache = PeerRowCache()

    if peer_type is not None:
        peer_cache.remember((utils.get_channel_id(77), 1, peer_type))

    return SimpleNamespace(storage=SimpleNamespace(_peer_cache=peer_cache), message_cache={})


@pytest.mark.parametrize(
    "peer_type, expected",
    [
        ("supergroup", enums.ChatType.SUPERGROUP),
        ("forum", enums.ChatType.FORUM),
        ("channel", enums.ChatType.CHANNEL),
        (None, enums.ChatType.CHANNEL),
    ],
)
async def test_deleted_channel_messages_use_stored_peer_type(peer_type, expected):
    client = deleted_channel_update_client(peer_type)
    update = raw.types.UpdateDeleteChannelMessages(channel_id=77, messages=[3], pts=1, pts_count=1)

    parsed = utils.parse_deleted_messages(client, update, {}, {})

    assert parsed[0].chat.id == utils.get_channel_id(77)
    assert parsed[0].chat.type is expected
    assert await filters.group(client, parsed[0]) is (
        expected in (enums.ChatType.SUPERGROUP, enums.ChatType.FORUM)
    )


async def test_deleted_channel_messages_prefer_chats_map():
    client = SimpleNamespace(storage=SimpleNamespace(), message_cache={})
    channel = raw.types.Channel(
        id=77,
        title="g",
        photo=raw.types.ChatPhotoEmpty(),
        date=0,
        megagroup=True,
        access_hash=1,
        usernames=[],
        restriction_reason=[],
    )
    update = raw.types.UpdateDeleteChannelMessages(channel_id=77, messages=[3], pts=1, pts_count=1)

    parsed = utils.parse_deleted_messages(client, update, {}, {77: channel})

    assert parsed[0].chat.type is enums.ChatType.SUPERGROUP


@pytest.mark.parametrize(
    "identifier",
    [
        {"chat_id": 100, "message_id": 5, "user_id": 1},
        {"message_id": 5, "user_id": 1},
        {"inline_message_id": "abc", "user_id": 1},
    ],
)
async def test_pinned_callback_listener_alerts_stranger(identifier):
    loop = asyncio.get_running_loop()
    client = SimpleNamespace(
        loop=loop, max_listeners=None, unallowed_click_alert=True, unallowed_click_alert_text="nope"
    )
    registry = ListenerRegistry(client)
    future = loop.create_future()
    listener = types.Listener(
        listener_type=enums.ListenerTypes.CALLBACK_QUERY,
        identifier=types.Identifier(**identifier),
        future=future,
        unallowed_click_alert=True,
    )
    registry.add(listener, None)

    answered = []

    async def answer(text=None, *args, **kwargs):
        answered.append(text)

    def query(user_id):
        return SimpleNamespace(
            message=SimpleNamespace(chat=SimpleNamespace(id=100), id=5),
            from_user=SimpleNamespace(id=user_id),
            inline_message_id=identifier.get("inline_message_id"),
            answer=answer,
        )

    assert await registry.feed(client, enums.ListenerTypes.CALLBACK_QUERY, query(999))
    assert answered == ["nope"]
    assert not future.done()

    owner_query = query(1)

    assert await registry.feed(client, enums.ListenerTypes.CALLBACK_QUERY, owner_query)
    assert future.result() is owner_query


def command_client(username="WzgramBot"):
    return SimpleNamespace(me=SimpleNamespace(username=username))


@pytest.mark.parametrize(
    "text, matched",
    [
        ("/start", True),
        ("/start@wzgrambot x", True),
        ("/start@WZGRAMBOT", True),
        ("/startwzgrambot", False),
        ("/start@otherbot", False),
    ],
)
async def test_command_requires_at_before_username(text, matched):
    assert (
        await filters.command("start")(command_client(), types.Message(id=1, text=text)) is matched
    )


async def test_case_sensitive_command_ignores_username_case():
    f = filters.command("start", case_sensitive=True)
    message = types.Message(id=1, text="/start@WZGRAMBOT a")

    assert await f(command_client(), message)
    assert message.command == ["start", "a"]
    assert not await f(command_client(), types.Message(id=1, text="/START@wzgrambot"))


async def test_command_without_username_rejects_bare_at():
    assert not await filters.command("start")(
        command_client(None), types.Message(id=1, text="/start@ x")
    )


@pytest.mark.parametrize(
    "pattern, data, matched",
    [
        (r"^a(\d)", b"\xff\x00a1", False),
        (rb"a1", "a1", False),
        (rb"a1", b"\xff\x00a1", True),
        (r"^a(\d)", "a1", True),
    ],
)
async def test_regex_on_callback_data_type_mismatch(pattern, data, matched):
    query = types.CallbackQuery(client=None, id="1", from_user=None, chat_instance="1", data=data)

    assert await filters.regex(pattern)(None, query) is matched


def test_bot_method_return_docs_match_behaviour():
    assert (
        "ChatPrivileges"
        in GetBotDefaultPrivileges.get_bot_default_privileges.__doc__.split("Returns:")[1]
    )
    assert inspect.signature(CheckBotUsername.check_bot_username).return_annotation in (
        bool,
        "bool",
    )
