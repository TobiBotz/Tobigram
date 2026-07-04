import pytest

from pyrogram.enums import MessageEntityType
from pyrogram.parser.markdown import (
    BOLD_DELIM,
    CODE_DELIM,
    ITALIC_DELIM,
    PRE_DELIM,
    SPOILER_DELIM,
    STRIKE_DELIM,
    UNDERLINE_DELIM,
    Markdown,
)
from pyrogram.raw.types import (
    InputMessageEntityMentionName,
    MessageEntityBold,
    MessageEntityCode,
    MessageEntityItalic,
    MessageEntityPre,
    MessageEntitySpoiler,
    MessageEntityStrike,
    MessageEntityTextUrl,
    MessageEntityUnderline,
)


@pytest.fixture
def markdown():
    return Markdown(None)


@pytest.mark.asyncio
class TestMarkdownParse:
    async def test_bold(self, markdown):
        result = await markdown.parse(f"Hello {BOLD_DELIM}world{BOLD_DELIM}")
        assert result["message"] == "Hello world"
        assert len(result["entities"]) == 1
        assert isinstance(result["entities"][0], MessageEntityBold)
        assert result["entities"][0].offset == 6
        assert result["entities"][0].length == 5

    async def test_italic(self, markdown):
        result = await markdown.parse(f"Hello {ITALIC_DELIM}world{ITALIC_DELIM}")
        assert result["message"] == "Hello world"
        assert isinstance(result["entities"][0], MessageEntityItalic)

    async def test_underline(self, markdown):
        result = await markdown.parse(f"Hello {UNDERLINE_DELIM}world{UNDERLINE_DELIM}")
        assert result["message"] == "Hello world"
        assert isinstance(result["entities"][0], MessageEntityUnderline)

    async def test_strike(self, markdown):
        result = await markdown.parse(f"Hello {STRIKE_DELIM}world{STRIKE_DELIM}")
        assert result["message"] == "Hello world"
        assert isinstance(result["entities"][0], MessageEntityStrike)

    async def test_spoiler(self, markdown):
        result = await markdown.parse(f"Hello {SPOILER_DELIM}world{SPOILER_DELIM}")
        assert result["message"] == "Hello world"
        assert isinstance(result["entities"][0], MessageEntitySpoiler)

    async def test_code(self, markdown):
        result = await markdown.parse(f"Hello {CODE_DELIM}code{CODE_DELIM}")
        assert result["message"] == "Hello code"
        assert isinstance(result["entities"][0], MessageEntityCode)

    async def test_pre(self, markdown):
        result = await markdown.parse(f"Hello {PRE_DELIM}\ncode\n{PRE_DELIM}")
        assert result["message"] == "Hello \ncode"
        assert isinstance(result["entities"][0], MessageEntityPre)
        assert result["entities"][0].offset == 6
        assert result["entities"][0].length == 5

    async def test_pre_with_language(self, markdown):
        result = await markdown.parse(f"```python\nprint('hi')\n```")
        assert isinstance(result["entities"][0], MessageEntityPre)
        assert result["entities"][0].language == "python"

    async def test_text_link(self, markdown):
        result = await markdown.parse("Hello [click](https://example.com)")
        assert result["message"] == "Hello click"
        assert isinstance(result["entities"][0], MessageEntityTextUrl)
        assert result["entities"][0].url == "https://example.com"

    async def test_nested(self, markdown):
        result = await markdown.parse(f"**bold __italic__**")
        assert result["message"] == "bold italic"

    async def test_strict_escapes_html(self, markdown):
        result = await markdown.parse("<script>alert(1)</script>", strict=True)
        assert result["entities"] is None
        assert result["message"] == "<script>alert(1)</script>"

    async def test_empty_text(self, markdown):
        result = await markdown.parse("")
        assert result["message"] == ""
        assert result["entities"] is None

    async def test_no_formatting(self, markdown):
        result = await markdown.parse("plain text")
        assert result["message"] == "plain text"
        assert result["entities"] is None


class TestMarkdownUnparse:
    def test_bold(self):
        class Entity:
            type = MessageEntityType.BOLD
            offset = 0
            length = 5

        result = Markdown.unparse("Hello", [Entity()])
        assert BOLD_DELIM in result
        assert result == f"{BOLD_DELIM}Hello{BOLD_DELIM}"

    def test_italic(self):
        class Entity:
            type = MessageEntityType.ITALIC
            offset = 0
            length = 5

        result = Markdown.unparse("Hello", [Entity()])
        assert result == f"{ITALIC_DELIM}Hello{ITALIC_DELIM}"

    def test_underline(self):
        class Entity:
            type = MessageEntityType.UNDERLINE
            offset = 0
            length = 5

        result = Markdown.unparse("Hello", [Entity()])
        assert result == f"{UNDERLINE_DELIM}Hello{UNDERLINE_DELIM}"

    def test_strikethrough(self):
        class Entity:
            type = MessageEntityType.STRIKETHROUGH
            offset = 0
            length = 5

        result = Markdown.unparse("Hello", [Entity()])
        assert result == f"{STRIKE_DELIM}Hello{STRIKE_DELIM}"

    def test_code(self):
        class Entity:
            type = MessageEntityType.CODE
            offset = 0
            length = 5

        result = Markdown.unparse("Hello", [Entity()])
        assert result == f"{CODE_DELIM}Hello{CODE_DELIM}"

    def test_pre(self):
        class Entity:
            type = MessageEntityType.PRE
            offset = 0
            length = 5
            language = "python"

        result = Markdown.unparse("Hello", [Entity()])
        assert result.startswith(f"{PRE_DELIM}python\n")
        assert result.endswith(f"\n{PRE_DELIM}")

    def test_pre_no_language(self):
        class Entity:
            type = MessageEntityType.PRE
            offset = 0
            length = 5
            language = ""

        result = Markdown.unparse("Hello", [Entity()])
        assert result == f"{PRE_DELIM}\nHello\n{PRE_DELIM}"

    def test_spoiler(self):
        class Entity:
            type = MessageEntityType.SPOILER
            offset = 0
            length = 5

        result = Markdown.unparse("Hello", [Entity()])
        assert result == f"{SPOILER_DELIM}Hello{SPOILER_DELIM}"

    def test_text_link(self):
        class Entity:
            type = MessageEntityType.TEXT_LINK
            offset = 0
            length = 5
            url = "https://example.com"

        result = Markdown.unparse("Hello", [Entity()])
        assert result == "[Hello](https://example.com)"

    def test_text_mention(self):
        class Entity:
            type = MessageEntityType.TEXT_MENTION
            offset = 0
            length = 5

            class user:
                id = 12345

        result = Markdown.unparse("Hello", [Entity()])
        assert result == "[Hello](tg://user?id=12345)"

    def test_unsupported_entity_skipped(self):
        class Entity:
            type = MessageEntityType.CUSTOM_EMOJI
            offset = 0
            length = 5
            custom_emoji_id = 123

        result = Markdown.unparse("Hello", [Entity()])
        assert result == "Hello"

    def test_multiple_entities(self):
        class EntityBold:
            type = MessageEntityType.BOLD
            offset = 0
            length = 5

        class EntityItalic:
            type = MessageEntityType.ITALIC
            offset = 6
            length = 4

        result = Markdown.unparse("Hello test", [EntityBold(), EntityItalic()])
        assert BOLD_DELIM in result
        assert ITALIC_DELIM in result
