import pytest

from pyrogram.parser.markdown import Markdown
from pyrogram.types import MessageEntity


async def parse(text):
    return await Markdown(None).parse(text)


def shape(parsed):
    return [
        (type(e).__name__, e.offset, e.length) for e in (parsed["entities"] or [])
    ]


def quote_of(parsed):
    return parsed["entities"][0]


async def test_a_quoted_line_becomes_a_blockquote():
    parsed = await parse(">quoted line")

    assert parsed["message"] == "quoted line"
    assert shape(parsed) == [("MessageEntityBlockquote", 0, len("quoted line"))]


async def test_neighbouring_quoted_lines_are_one_blockquote():
    parsed = await parse(">line one\n>line two")

    assert parsed["message"] == "line one\nline two"
    assert shape(parsed) == [("MessageEntityBlockquote", 0, len("line one\nline two"))]


async def test_a_quote_ends_at_the_first_unquoted_line():
    parsed = await parse(">quoted\nplain")

    assert parsed["message"] == "quoted\nplain"
    assert shape(parsed) == [("MessageEntityBlockquote", 0, len("quoted"))]


async def test_an_expandable_quote_is_marked_collapsed():
    parsed = await parse("**>expandable line||")

    assert parsed["message"] == "expandable line"
    assert quote_of(parsed).collapsed is True


async def test_an_expandable_quote_spans_its_quoted_lines():
    parsed = await parse("**>line one\n>line two||")

    assert parsed["message"] == "line one\nline two"
    quote = quote_of(parsed)
    assert quote.collapsed is True
    assert quote.length == len("line one\nline two")


async def test_formatting_inside_a_quote_still_applies():
    parsed = await parse(">quoted **bold** here")

    assert parsed["message"] == "quoted bold here"
    assert shape(parsed) == [
        ("MessageEntityBlockquote", 0, len("quoted bold here")),
        ("MessageEntityBold", 7, 4),
    ]


async def test_a_marker_that_does_not_start_a_line_is_text():
    parsed = await parse("a > b")

    assert parsed["message"] == "a > b"
    assert not parsed["entities"]


async def test_a_marker_inside_a_code_block_is_text():
    parsed = await parse("```\n>not a quote\n```")

    assert ">not a quote" in parsed["message"]
    assert [name for name, _, _ in shape(parsed)] == ["MessageEntityPre"]


@pytest.mark.parametrize(
    "source",
    [
        ">quoted line",
        ">line one\n>line two",
        "**>expandable line||",
        "**>line one\n>line two||",
        ">quoted **bold** here",
    ],
)
async def test_a_quote_survives_being_rendered_and_read_again(source):
    parsed = await parse(source)
    entities = [MessageEntity._parse(None, e, {}) for e in parsed["entities"]]
    rendered = Markdown.unparse(parsed["message"], entities)

    assert rendered == source, (
        "unparse writes what parse must be able to read back, or a quote is "
        "silently lost every time a message is rendered and re-sent"
    )

    again = await parse(rendered)
    assert again["message"] == parsed["message"]
    assert shape(again) == shape(parsed)
