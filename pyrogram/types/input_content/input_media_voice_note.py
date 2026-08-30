#  Pyrogram - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-present Dan <https://github.com/delivrance>
#
#  This file is part of Pyrogram.
#
#  Pyrogram is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Pyrogram is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with Pyrogram.  If not, see <http://www.gnu.org/licenses/>.

import io
import pathlib
import re
from typing import BinaryIO, Callable, List, Optional, Union

import pyrogram
from pyrogram import raw, utils
from pyrogram.file_id import FileType

from ... import enums
from ..messages_and_media import MessageEntity
from .input_media import InputMedia


class InputMediaVoiceNote(InputMedia):
    """A voice message to be sent.

    Use this class to send a voice note (audio recording) to a chat.
    The voice note is uploaded to Telegram servers and sent as a
    document with a voice attribute.

    Parameters:
        media (``str`` | ``BinaryIO``):
            Voice note to send.
            Pass a file_id as string to send a voice note that exists on the Telegram servers or
            pass a file path as string to upload a new voice note that exists on your local machine or
            pass a binary file-like object with its attribute ".name" set for in-memory uploads or
            pass an HTTP URL as a string for Telegram to get a voice note from the Internet.

        duration (``int``, *optional*):
            Duration of the voice note in seconds.

        waveform (``bytes``, *optional*):
            Waveform representation of the voice note, as a byte string.
            Used by clients to render the audio waveform visualization.

        caption (``str``, *optional*):
            Caption of the voice note to be sent, 0-1024 characters.
            If not specified, the original caption is kept. Pass "" (empty string) to remove the caption.

        parse_mode (:obj:`~pyrogram.enums.ParseMode`, *optional*):
            By default, texts are parsed using both Markdown and HTML styles.
            You can combine both syntaxes together.

        caption_entities (List of :obj:`~pyrogram.types.MessageEntity`):
            List of special entities that appear in the caption, which can be specified instead of *parse_mode*.

        file_name (``str``, *optional*):
            File name of the voice note sent.
            Defaults to file's path basename.

    Example:
        .. code-block:: python

            from wzgram.types import InputMediaVoiceNote

            # Send a voice note by file path
            voice = InputMediaVoiceNote(media="voice.ogg", duration=30)

            # Send a voice note by file_id
            voice = InputMediaVoiceNote(media="<file_id>")
    """

    def __init__(
        self,
        media: Union[str, BinaryIO],
        duration: int = 0,
        waveform: Optional[bytes] = None,
        caption: str = "",
        parse_mode: Optional["enums.ParseMode"] = None,
        caption_entities: Optional[List[MessageEntity]] = None,
        file_name: Optional[str] = None
    ):
        super().__init__(media, caption, parse_mode, caption_entities)

        self.duration = duration
        self.waveform = waveform
        self.file_name = file_name

    async def write(
        self,
        *,
        client: "pyrogram.Client",
        chat_id: Optional[Union[int, str]] = None,
        progress: Optional[Callable] = None,
        progress_args: tuple = (),
        ttl_seconds: Optional[int] = None,
        **kwargs
    ) -> "raw.base.InputMedia":
        if chat_id is None:
            peer = raw.types.InputPeerSelf()
        else:
            peer = await client.resolve_peer(chat_id)

        if isinstance(self.media, io.BytesIO) or pathlib.Path(self.media).is_file():
            mime_type = client.guess_mime_type(self.media) or "audio/ogg"

            if mime_type == "audio/ogg":
                mime_type = "audio/opus"

            uploaded_media = await client.invoke(
                raw.functions.messages.UploadMedia(
                    peer=peer,
                    media=raw.types.InputMediaUploadedDocument(
                        mime_type=mime_type,
                        file=await client.save_file(
                            self.media, progress=progress, progress_args=progress_args
                        ),
                        attributes=[
                            raw.types.DocumentAttributeAudio(
                                duration=self.duration,
                                voice=True,
                                waveform=self.waveform,
                            ),
                            raw.types.DocumentAttributeFilename(
                                file_name=utils.get_file_name(
                                    self.media, file_name=self.file_name, fallback="voice.ogg"
                                ),
                            ),
                        ],
                        ttl_seconds=ttl_seconds,
                    ),
                ),
            )

            return raw.types.InputMediaDocument(
                id=raw.types.InputDocument(
                    id=uploaded_media.document.id,
                    access_hash=uploaded_media.document.access_hash,
                    file_reference=uploaded_media.document.file_reference,
                ),
            )

        if re.match("^https?://", self.media):
            return raw.types.InputMediaDocumentExternal(
                url=self.media,
                ttl_seconds=ttl_seconds,
            )

        return utils.get_input_media_from_file_id(self.media, FileType.AUDIO, ttl_seconds=ttl_seconds)
