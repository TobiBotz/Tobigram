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

from __future__ import annotations

from typing import BinaryIO

import pyrogram
from pyrogram import raw, types


class UploadStickerFile:
    async def upload_sticker_file(
        self: pyrogram.Client,
        user_id: int | str,
        sticker: str | BinaryIO,
        sticker_format: str = "static",
    ) -> types.Document:
        """Upload a file with a sticker for later use in :meth:`~Client.create_sticker_set`.

        Returns the uploaded file as a :obj:`~pyrogram.types.Document`.

        .. include:: /_includes/usable-by/bots.rst

        Parameters:
            user_id (``int`` | ``str``):
                User identifier of the sticker file owner.

            sticker (``str`` | ``BinaryIO``):
                A file path (str) or a file-like object (BinaryIO) of the sticker to upload.
                For static stickers use .WEBP or .PNG; for animated use .TGS;
                for video use .WEBM.

            sticker_format (``str``, *optional*):
                Format of the sticker: ``"static"``, ``"animated"``, or ``"video"``.
                Defaults to ``"static"``.

        Returns:
            :obj:`~pyrogram.types.Document`: The uploaded sticker file as a Document.

        Example:
            .. code-block:: python

                doc = await app.upload_sticker_file(user_id, "sticker.webp")
                print(doc.file_id)
        """
        if isinstance(sticker, str):
            with open(sticker, "rb") as f:
                file = await self.save_file(f)
        else:
            file = await self.save_file(sticker)

        # Determine the MIME type and attributes based on format
        if sticker_format == "animated":
            mime_type = "application/x-tgsticker"
            attributes = [raw.types.DocumentAttributeFilename(file_name="sticker.tgs")]
        elif sticker_format == "video":
            mime_type = "video/webm"
            attributes = [
                raw.types.DocumentAttributeFilename(file_name="sticker.webm"),
                raw.types.DocumentAttributeVideo(
                    duration=0,
                    w=512,
                    h=512,
                    nosound=True,
                ),
            ]
        else:
            mime_type = "image/webp"
            attributes = [raw.types.DocumentAttributeFilename(file_name="sticker.webp")]

        r = await self.invoke(
            raw.functions.messages.UploadMedia(
                peer=await self.resolve_peer(user_id),
                media=raw.types.InputMediaUploadedDocument(
                    file=file,
                    mime_type=mime_type,
                    attributes=attributes,
                    stickers=None,
                    nosound_video=None,
                    force_file=None,
                    ttl_seconds=None,
                    spoiler=None,
                ),
            )
        )

        return types.Document._parse(self, r.document, None, None)
