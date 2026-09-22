import base64
import struct

import pytest

from pyrogram import enums, raw, types
from pyrogram.methods.messages import edit_inline_text as module
from pyrogram.parser import Parser

INLINE_MESSAGE_ID = base64.urlsafe_b64encode(struct.pack("<iqq", 2, 123, 456)).decode().rstrip("=")


class FakeClient:
    link_preview_options = None
    parse_mode = None
    parser = Parser(None)


@pytest.fixture
def sent(monkeypatch):
    calls = {}

    async def invoke_inline(client, dc_id, query, business_connection_id):
        calls["dc_id"] = dc_id
        calls["query"] = query
        return True

    monkeypatch.setattr(module, "invoke_inline", invoke_inline)

    return calls


async def edit(**kwargs):
    return await module.EditInlineText.edit_inline_text(FakeClient(), INLINE_MESSAGE_ID, **kwargs)


@pytest.mark.asyncio
async def test_markdown_rich_text_becomes_a_rich_message(sent):
    await edit(rich_text="# Title\n\n**bold**")

    query = sent["query"]

    assert isinstance(query.rich_message, raw.types.InputRichMessageMarkdown)
    assert query.rich_message.markdown == "# Title\n\n**bold**"
    assert query.message == ""
    assert sent["dc_id"] == 2


@pytest.mark.asyncio
async def test_html_rich_text_becomes_a_rich_message(sent):
    await edit(rich_text="<h2>Title</h2>", rich_text_parse_mode=enums.ParseMode.HTML)

    assert isinstance(sent["query"].rich_message, raw.types.InputRichMessageHTML)


@pytest.mark.asyncio
async def test_an_input_rich_message_is_written_as_given(sent):
    await edit(rich_text=types.InputRichMessage(html="<p>x</p>"))

    assert isinstance(sent["query"].rich_message, raw.types.InputRichMessageHTML)


@pytest.mark.asyncio
async def test_plain_text_is_untouched(sent):
    await edit(text="plain **bold**")

    query = sent["query"]

    assert query.rich_message is None
    assert query.message == "plain bold"
    assert query.entities


@pytest.mark.asyncio
async def test_neither_text_nor_rich_text_raises(sent):
    with pytest.raises(ValueError):
        await edit()


class StubClient:
    business_connection_id = None
    parse_mode = None

    def __init__(self):
        self.calls = {}

    def __getattr__(self, name):
        async def call(**kwargs):
            self.calls[name] = kwargs
            return "edited"

        return call


def a_message(client):
    from pyrogram import enums as _enums
    from pyrogram.types import Chat, Message

    return Message(
        id=7,
        chat=Chat(id=11, type=_enums.ChatType.PRIVATE, client=client),
        client=client,
    )


@pytest.mark.asyncio
async def test_message_edit_text_forwards_rich_text():
    client = StubClient()

    await a_message(client).edit_text(rich_text="# hi", rich_text_parse_mode=enums.ParseMode.HTML)

    sent = client.calls["edit_message_text"]

    assert sent["rich_text"] == "# hi"
    assert sent["rich_text_parse_mode"] is enums.ParseMode.HTML
    assert sent["text"] is None


@pytest.mark.asyncio
async def test_callback_query_edits_a_chat_message_with_rich_text():
    from pyrogram.types import CallbackQuery, User

    client = StubClient()
    query = CallbackQuery(
        id="1",
        from_user=User(id=1, client=client),
        chat_instance="x",
        message=a_message(client),
        client=client,
    )

    await query.edit_message_text(rich_text="# hi")

    assert client.calls["edit_message_text"]["rich_text"] == "# hi"


@pytest.mark.asyncio
async def test_callback_query_edits_an_inline_message_with_rich_text():
    from pyrogram.types import CallbackQuery, User

    client = StubClient()
    query = CallbackQuery(
        id="1",
        from_user=User(id=1, client=client),
        chat_instance="x",
        inline_message_id=INLINE_MESSAGE_ID,
        client=client,
    )

    await query.edit_message_text(rich_text="# hi")

    assert client.calls["edit_inline_text"]["rich_text"] == "# hi"


@pytest.mark.asyncio
async def test_message_edit_ephemeral_text_keeps_the_old_name_working():
    from pyrogram.types import User

    client = StubClient()
    message = a_message(client)
    message.ephemeral_message_id = 3
    message.receiver_user = User(id=5, client=client)
    rich = types.InputRichMessage(markdown="# hi")

    await message.edit_ephemeral_text(rich_message=rich)

    assert client.calls["edit_ephemeral_message_text"]["rich_message"] is rich


@pytest.mark.asyncio
async def test_the_deprecated_name_still_reaches_the_wire(monkeypatch):
    import pyrogram
    from pyrogram.methods.ephemeral import edit_ephemeral_message_text as ephemeral

    seen = {}

    async def edit_ephemeral(client, chat_id, receiver_id, message_id, **kwargs):
        seen.update(kwargs)
        return None

    monkeypatch.setattr(ephemeral, "edit_ephemeral", edit_ephemeral)

    await pyrogram.Client.edit_ephemeral_message_text(
        FakeClient(), 1, 2, 3, rich_message=types.InputRichMessage(markdown="# hi")
    )

    assert isinstance(seen["rich_message"], raw.types.InputRichMessageMarkdown)
    assert seen["rich_message"].markdown == "# hi"


@pytest.mark.asyncio
async def test_build_input_rich_message_picks_the_constructor_by_parse_mode():
    from pyrogram import utils

    client = FakeClient()

    assert isinstance(
        await utils.build_input_rich_message(client, "# hi"),
        raw.types.InputRichMessageMarkdown,
    )
    assert isinstance(
        await utils.build_input_rich_message(client, "<h1>hi</h1>", enums.ParseMode.HTML),
        raw.types.InputRichMessageHTML,
    )
    assert isinstance(
        await utils.build_input_rich_message(client, types.InputRichMessage(html="<p>x</p>")),
        raw.types.InputRichMessageHTML,
    )
