import io
from unittest.mock import AsyncMock

import pytest

from pyrogram import enums, raw, types, utils
from pyrogram.methods.messages.delete_scheduled_messages import DeleteScheduledMessages
from pyrogram.methods.messages.edit_message_text import EditMessageText
from pyrogram.methods.messages.get_scheduled_messages import GetScheduledMessages
from pyrogram.methods.messages.send_media_group import SendMediaGroup
from pyrogram.methods.messages.send_message import SendMessage
from pyrogram.methods.messages.send_venue import SendVenue
from pyrogram.parser.markdown import Markdown
from pyrogram.parser.parser import Parser


def _empty_updates():
    return raw.types.Updates(updates=[], users=[], chats=[], date=0, seq=0)


class _Client(SendMediaGroup, SendMessage, SendVenue, EditMessageText,
              GetScheduledMessages, DeleteScheduledMessages):
    parse_mode = enums.ParseMode.MARKDOWN
    link_preview_options = None
    me = None

    def __init__(self, reply=None):
        self.sent = []
        self.reply = reply if reply is not None else _empty_updates()
        self.parser = Parser(self)

    async def resolve_peer(self, peer_id):
        return raw.types.InputPeerSelf()

    def rnd_id(self):
        return 1

    def guess_mime_type(self, filename):
        return None

    async def save_file(self, path, *args, **kwargs):
        return raw.types.InputFile(id=1, parts=1, name="x", md5_checksum="") if path else None

    async def invoke(self, query, *args, **kwargs):
        self.sent.append(query)

        if isinstance(query, raw.functions.messages.UploadMedia):
            return raw.types.MessageMediaDocument(
                document=raw.types.Document(
                    id=1, access_hash=2, file_reference=b"", date=0, mime_type="",
                    size=1, dc_id=2, attributes=[], thumbs=[], video_thumbs=[]
                )
            )

        return self.reply


def _message(client):
    message = types.Message(id=7, chat=object.__new__(type("C", (), {"id": -100})))
    message._client = client

    return message


async def test_a_reply_shortcut_forwards_its_legacy_reply_and_quote_kwargs():
    client = type("C", (), {"send_message": AsyncMock()})()
    message = _message(client)

    await message.reply("hi", reply_to_message_id=5, quote_text="q")

    params = client.send_message.call_args.kwargs["reply_parameters"]
    assert (params.message_id, params.quote) == (5, "q"), (
        "the default ReplyParameters must carry the legacy kwargs; send_message "
        "ignores them once reply_parameters is set"
    )

    await message.reply("hi")
    assert client.send_message.call_args.kwargs["reply_parameters"].message_id == 7


async def test_a_grouped_audio_or_document_keeps_its_file_name():
    client = _Client()

    await client.send_media_group("me", [
        types.InputMediaAudio(io.BytesIO(b"a"), file_name="song.ogg"),
        types.InputMediaDocument(io.BytesIO(b"d"), file_name="notes.txt"),
    ])

    uploads = [q.media for q in client.sent if isinstance(q, raw.functions.messages.UploadMedia)]
    names = [
        a.file_name for m in uploads for a in m.attributes
        if isinstance(a, raw.types.DocumentAttributeFilename)
    ]
    assert names == ["song.ogg", "notes.txt"]


async def test_a_grouped_document_is_forced_to_stay_a_file():
    client = _Client()

    await client.send_media_group("me", [
        types.InputMediaDocument(io.BytesIO(b"d")),
        types.InputMediaDocument(io.BytesIO(b"d"), disable_content_type_detection=False),
    ])

    uploads = [q.media for q in client.sent if isinstance(q, raw.functions.messages.UploadMedia)]
    assert [m.force_file for m in uploads] == [True, False]


