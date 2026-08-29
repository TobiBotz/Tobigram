import ast
from pathlib import Path

import pytest

from pyrogram import raw, types

PYROGRAM = Path(__file__).resolve().parents[1] / "pyrogram"


def photo(n: int = 1) -> "raw.types.InputPhoto":
    return raw.types.InputPhoto(id=n, access_hash=n, file_reference=b"")


def document(n: int = 1) -> "raw.types.InputDocument":
    return raw.types.InputDocument(id=n, access_hash=n, file_reference=b"")


def test_block_message_has_no_trailing_vectors():
    for media in (None, types.InputRichMessageMedia(photos=[])):
        b = types.InputRichMessage(
            blocks=[types.InputRichBlockDivider()], media=media
        ).write().write()
        assert len(b) == 20, b.hex()


@pytest.mark.parametrize("kwargs,expected", [
    ({"html": '<img src="tg://photo?id=pic">'}, raw.types.InputRichMessageHTML),
    ({"markdown": "![](tg://photo?id=pic)"}, raw.types.InputRichMessageMarkdown),
])
def test_media_reaches_html_and_markdown(kwargs, expected):
    written = types.InputRichMessage(
        media=[types.InputRichMessageMedia(id="pic", media=photo())],
        **kwargs,
    ).write()

    assert isinstance(written, expected)
    assert written.files == [raw.types.InputRichFilePhoto(id="pic", photo=photo())], (
        "tg://photo?id= resolves against the files vector, so a message whose "
        "files are dropped can never show its media"
    )


def test_a_document_becomes_a_rich_file_document():
    written = types.InputRichMessage(
        html="x", media=types.InputRichMessageMedia(id="vid", media=document())
    ).write()

    assert written.files == [raw.types.InputRichFileDocument(id="vid", document=document())]


def test_no_media_leaves_the_files_vector_absent():
    written = types.InputRichMessage(html="x").write()

    assert written.files is None, "an empty vector is not the same as an absent flag"


def test_an_id_the_server_will_not_accept_is_refused():
    with pytest.raises(ValueError, match="Invalid media id"):
        types.InputRichMessageMedia(id="not a valid id!", media=photo()).write_file()


def test_media_that_still_needs_uploading_says_so():
    with pytest.raises(ValueError, match="already exists on Telegram"):
        types.InputRichMessageMedia(id="pic", media=object()).write_file()


def test_block_vectors_merge_across_a_media_list():
    written = types.InputRichMessage(
        blocks=[types.InputRichBlockDivider()],
        media=[
            types.InputRichMessageMedia(photos=[photo(1)]),
            types.InputRichMessageMedia(photos=[photo(2)], documents=[document(3)]),
        ],
    ).write()

    assert written.photos == [photo(1), photo(2)]
    assert written.documents == [document(3)]


def _rich_message_constructions():
    for path in sorted((PYROGRAM / "methods").rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))

        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue

            name = getattr(node.func, "attr", None)

            if name in ("InputRichMessageHTML", "InputRichMessageMarkdown"):
                yield path, node


def test_every_send_path_threads_the_files_vector():
    calls = list(_rich_message_constructions())

    assert calls, "this guard is pointless if nothing builds a rich message"

    for path, node in calls:
        keywords = {kw.arg for kw in node.keywords}

        assert "files" in keywords, (
            f"{path.name}:{node.lineno} builds a rich message without files=, so "
            "media referenced from the text can never resolve"
        )


def test_an_ordered_list_uses_the_ordered_item_constructors():
    """pageBlockOrderedList takes Vector<PageListOrderedItem>, a different base
    type from the Vector<PageListItem> an unordered list takes. Feeding it plain
    page list items put the wrong constructor on the wire and Telegram answered
    RICH_MESSAGE_BLOCK_UNEXPECTED, so an ordered list could never be sent."""
    block = types.InputRichBlockList(
        items=[
            types.InputRichBlockListItem(text="first"),
            types.InputRichBlockListItem(text="done", has_checkbox=True, is_checked=True),
            types.InputRichBlockListItem(
                blocks=[types.InputRichBlockParagraph(text="nested")]
            ),
        ],
        ordered=True,
    ).write()

    assert isinstance(block, raw.types.PageBlockOrderedList)
    assert [type(item) for item in block.items] == [
        raw.types.PageListOrderedItemText,
        raw.types.PageListOrderedItemText,
        raw.types.PageListOrderedItemBlocks,
    ]
    assert block.items[1].checkbox and block.items[1].checked
    block.write()


def test_an_unordered_list_keeps_the_plain_item_constructors():
    block = types.InputRichBlockList(
        items=[
            types.InputRichBlockListItem(text="first"),
            types.InputRichBlockListItem(
                blocks=[types.InputRichBlockParagraph(text="nested")]
            ),
        ]
    ).write()

    assert isinstance(block, raw.types.PageBlockList)
    assert [type(item) for item in block.items] == [
        raw.types.PageListItemText,
        raw.types.PageListItemBlocks,
    ]
    block.write()
