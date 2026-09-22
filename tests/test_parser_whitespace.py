import pytest

from pyrogram import enums
from pyrogram.parser import Parser


async def parse(text, mode):
    return await Parser(None).parse(text, mode)


def shape(parsed):
    return [
        (type(e).__name__.replace("MessageEntity", "").lower(), e.offset, e.length)
        for e in (parsed["entities"] or [])
    ]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "source,message,entities",
    [
        (">a\n>b", "a\nb", [("blockquote", 0, 3)]),
        ("> a\n> b", " a\n b", [("blockquote", 0, 5)]),
        (">  a", "  a", [("blockquote", 0, 3)]),
        ("x\n> a\n> b", "x\n a\n b", [("blockquote", 2, 5)]),
        ("**> a\n> b||", " a\n b", [("blockquote", 0, 5)]),
    ],
)
async def test_markdown_keeps_the_space_after_the_quote_marker(source, message, entities):
    parsed = await parse(source, enums.ParseMode.MARKDOWN)

    assert parsed["message"] == message
    assert shape(parsed) == entities


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "source,message,entities",
    [
        ("<blockquote> a\n b</blockquote>", " a\n b", [("blockquote", 0, 5)]),
        ("<b> x</b>", " x", [("bold", 0, 2)]),
        ("<pre> x</pre>", " x", [("pre", 0, 2)]),
        ("  <b>x</b>  ", "x", [("bold", 0, 1)]),
        ("<b>x </b>", "x", [("bold", 0, 1)]),
        ("<b>x</b>\n\n", "x", [("bold", 0, 1)]),
        ("<b>x </b><i>y</i>", "x y", [("bold", 0, 2), ("italic", 2, 1)]),
        ("<b>  </b>", "", []),
    ],
)
async def test_html_whitespace_matches_what_telegram_stores(source, message, entities):
    parsed = await parse(source, enums.ParseMode.HTML)

    assert parsed["message"] == message
    assert shape(parsed) == entities
