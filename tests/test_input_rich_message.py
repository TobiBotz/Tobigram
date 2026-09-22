import ast
from pathlib import Path

import pytest

from pyrogram import raw, types, utils

PYROGRAM = Path(__file__).resolve().parents[1] / "pyrogram"


def photo(n: int = 1) -> "raw.types.InputPhoto":
    return raw.types.InputPhoto(id=n, access_hash=n, file_reference=b"")


def document(n: int = 1) -> "raw.types.InputDocument":
    return raw.types.InputDocument(id=n, access_hash=n, file_reference=b"")


def test_block_message_has_no_trailing_vectors():
    for media in (None, types.InputRichMessageMedia(photos=[])):
        b = (
            types.InputRichMessage(blocks=[types.InputRichBlockDivider()], media=media)
            .write()
            .write()
        )
        assert len(b) == 20, b.hex()


@pytest.mark.parametrize(
    "kwargs,expected",
    [
        ({"html": '<img src="tg://photo?id=pic">'}, raw.types.InputRichMessageHTML),
        ({"markdown": "![](tg://photo?id=pic)"}, raw.types.InputRichMessageMarkdown),
    ],
)
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
    paths = sorted((PYROGRAM / "methods").rglob("*.py")) + [PYROGRAM / "utils.py"]

    for path in paths:
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
            types.InputRichBlockListItem(blocks=[types.InputRichBlockParagraph(text="nested")]),
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
            types.InputRichBlockListItem(blocks=[types.InputRichBlockParagraph(text="nested")]),
        ]
    ).write()

    assert isinstance(block, raw.types.PageBlockList)
    assert [type(item) for item in block.items] == [
        raw.types.PageListItemText,
        raw.types.PageListItemBlocks,
    ]
    block.write()


def test_a_thinking_block_writes_the_page_block_the_tag_maps_to():
    written = types.InputRichMessage(
        blocks=[types.InputRichBlockThinking(text="Reading files")]
    ).write()

    assert written.blocks == [
        raw.types.PageBlockThinking(
            text=raw.types.TextConcat(texts=[raw.types.TextPlain(text="Reading files")])
        )
    ]


@pytest.mark.parametrize(
    "kwargs,expected,field",
    [
        (
            {"html": "<tg-thinking>Thinking...</tg-thinking>"},
            raw.types.InputRichMessageHTML,
            "html",
        ),
        (
            {"markdown": "<tg-thinking>Thinking...</tg-thinking>"},
            raw.types.InputRichMessageMarkdown,
            "markdown",
        ),
    ],
)
def test_the_thinking_tag_reaches_the_wire_untouched(kwargs, expected, field):
    written = types.InputRichMessage(**kwargs).write()

    assert isinstance(written, expected)
    assert getattr(written, field) == "<tg-thinking>Thinking...</tg-thinking>", (
        "the html and markdown forms are parsed by the server, so a tag the "
        "library rewrote or dropped could never render"
    )


class UploadingClient:
    def __init__(self):
        self.uploaded = []

    async def invoke(self, query, *args, **kwargs):
        self.uploaded.append(query)

        return raw.types.MessageMediaPhoto(
            photo=raw.types.Photo(
                id=111, access_hash=222, file_reference=b"fr", date=0, sizes=[], dc_id=2
            )
        )

    async def resolve_peer(self, peer_id):
        return raw.types.InputPeerUser(user_id=peer_id, access_hash=9)

    async def save_file(self, *args, **kwargs):
        return raw.types.InputFile(id=1, parts=1, name="x.png", md5_checksum="")


@pytest.mark.asyncio
async def test_a_block_uploads_the_photo_it_was_given():
    client = UploadingClient()

    message = types.InputRichMessage(
        blocks=[types.InputRichBlockPhoto(photo=types.InputMediaPhoto("README.md"))]
    )

    written = await utils.build_input_rich_message(client, message, chat_id=5)

    assert written.blocks[0].photo_id == 111
    assert [p.id for p in written.photos] == [111]
    assert written.documents is None


@pytest.mark.asyncio
async def test_a_block_mention_reaches_the_users_vector():
    client = UploadingClient()

    message = types.InputRichMessage(
        blocks=[
            types.InputRichBlockParagraph(
                text=raw.types.TextMentionName(user_id=777, text=raw.types.TextPlain(text="hi"))
            )
        ]
    )

    written = await utils.build_input_rich_message(client, message)

    assert [u.user_id for u in written.users] == [777]


@pytest.mark.asyncio
async def test_a_media_id_uploads_for_html_too():
    client = UploadingClient()

    message = types.InputRichMessage(
        html='<img src="tg://photo?id=a">',
        media=types.InputRichMessageMedia(id="a", media=types.InputMediaPhoto("README.md")),
    )

    written = await utils.build_input_rich_message(client, message)

    assert isinstance(written.files[0], raw.types.InputRichFilePhoto)
    assert written.files[0].photo.id == 111


@pytest.mark.asyncio
async def test_an_already_uploaded_block_photo_needs_no_round_trip():
    client = UploadingClient()

    message = types.InputRichMessage(
        blocks=[types.InputRichBlockPhoto(photo_id=42)],
        media=types.InputRichMessageMedia(photos=[photo(42)]),
    )

    written = await utils.build_input_rich_message(client, message)

    assert client.uploaded == []
    assert written.blocks[0].photo_id == 42


def test_a_media_block_without_media_is_refused():
    for block, kwargs in (
        (types.InputRichBlockPhoto, {}),
        (types.InputRichBlockVideo, {}),
        (types.InputRichBlockAnimation, {}),
        (types.InputRichBlockAudio, {}),
        (types.InputRichBlockVoiceNote, {}),
        (types.InputRichBlockDocument, {}),
    ):
        with pytest.raises(ValueError):
            block(**kwargs)
