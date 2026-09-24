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

import asyncio
import io
import os
import re
import urllib.request
from typing import BinaryIO, Optional
from collections.abc import Callable

import pyrogram
from pyrogram import enums, raw, types, utils
from pyrogram.file_id import FileType
from ..object import Object

MAX_DOWNLOAD_SIZE = 10 * 1024 * 1024


class InputSticker(Object):
    """A sticker to be added to a sticker set.

    Parameters:
        sticker (``str`` | ``BinaryIO``):
            The added sticker.
            Pass a file_id as string to use a file that exists on the Telegram servers,
            pass an HTTP URL as string to download the file and upload it,
            pass a file path as string to upload a new file that exists on your local machine or
            pass a binary file-like object with its attribute ".name" set for in-memory uploads.

        format (:obj:`~pyrogram.enums.StickerFormat`):
            Format of the added sticker.

        emoji_list (List of ``str``):
            List of 1-20 emoji associated with the sticker.

        mask_position (:obj:`~pyrogram.types.MaskPosition`, *optional*):
            Position where the mask should be placed on faces.
            For mask stickers only.

        keywords (List of ``str``, *optional*):
            List of 0-20 search keywords for the sticker with total length of up to 64 characters.
            For regular and custom emoji stickers only.
    """

    def __init__(
        self,
        sticker: str | BinaryIO,
        format: "enums.StickerFormat",
        emoji_list: list[str],
        mask_position: Optional["types.MaskPosition"] = None,
        keywords: list[str] | None = None,
    ):
        super().__init__()

        self.sticker = sticker
        self.format = format
        self.emoji_list = emoji_list
        self.mask_position = mask_position
        self.keywords = keywords

    async def _upload(
        self,
        client: "pyrogram.Client",
        chat_id: int | str | None = None,
        progress: Callable | None = None,
        progress_args: tuple = (),
    ) -> "raw.types.Document":
        if self.format == enums.StickerFormat.ANIMATED:
            file_name, mime_type = "sticker.tgs", "application/x-tgsticker"
        elif self.format == enums.StickerFormat.VIDEO:
            file_name, mime_type = "sticker.webm", "video/webm"
        else:
            file_name, mime_type = "sticker.png", "image/png"

        sticker = self.sticker

        if self._is_url():
            sticker = io.BytesIO(await asyncio.to_thread(self._download, sticker))
            sticker.name = file_name

        r = await client.invoke(
            raw.functions.messages.UploadMedia(
                peer=await client.resolve_peer(chat_id)
                if chat_id is not None
                else raw.types.InputPeerSelf(),
                media=raw.types.InputMediaUploadedDocument(
                    mime_type=mime_type,
                    file=await client.save_file(
                        sticker, progress=progress, progress_args=progress_args
                    ),
                    attributes=[
                        raw.types.DocumentAttributeFilename(file_name=file_name),
                        raw.types.DocumentAttributeSticker(
                            alt="".join(self.emoji_list),
                            stickerset=raw.types.InputStickerSetEmpty(),
                            mask=self.mask_position is not None,
                            mask_coords=self.mask_position.write() if self.mask_position else None,
                        ),
                    ],
                ),
            )
        )

        return r.document

    def _is_url(self) -> bool:
        return isinstance(self.sticker, str) and re.match("^https?://", self.sticker) is not None

    @staticmethod
    def _download(url: str) -> bytes:
        request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})

        with urllib.request.urlopen(request, timeout=30) as response:
            data = response.read(MAX_DOWNLOAD_SIZE + 1)

        if len(data) > MAX_DOWNLOAD_SIZE:
            raise ValueError(f"The sticker at {url} is larger than {MAX_DOWNLOAD_SIZE} bytes")

        return data

    def _is_upload(self) -> bool:
        return not isinstance(self.sticker, str) or self._is_url() or os.path.isfile(self.sticker)

    async def write(
        self,
        client: "pyrogram.Client",
        chat_id: int | str | None = None,
        progress: Callable | None = None,
        progress_args: tuple = (),
    ) -> "raw.types.InputStickerSetItem":
        if self._is_upload():
            document = await self._upload(client, chat_id, progress, progress_args)
            input_document = raw.types.InputDocument(
                id=document.id,
                access_hash=document.access_hash,
                file_reference=document.file_reference,
            )
        else:
            input_document = utils.get_input_media_from_file_id(self.sticker, FileType.STICKER).id

        return raw.types.InputStickerSetItem(
            document=input_document,
            emoji="".join(self.emoji_list),
            mask_coords=self.mask_position.write() if self.mask_position else None,
            keywords=",".join(self.keywords) if self.keywords else None,
        )
