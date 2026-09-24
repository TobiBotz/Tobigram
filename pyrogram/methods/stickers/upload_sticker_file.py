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
from pyrogram import enums, types
from pyrogram.file_id import FileId, FileType, FileUniqueId, FileUniqueType


class UploadStickerFile:
    async def upload_sticker_file(
        self: pyrogram.Client,
        user_id: int | str,
        sticker: str | BinaryIO,
        sticker_format: enums.StickerFormat,
    ) -> types.File:
        """Upload a file with a sticker for later use in :meth:`~pyrogram.Client.create_new_sticker_set`,
        :meth:`~pyrogram.Client.add_sticker_to_set` and :meth:`~pyrogram.Client.replace_sticker_in_set`.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            user_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the sticker set owner.

            sticker (``str`` | ``BinaryIO``):
                File path, HTTP URL or binary file-like object of the sticker, which must fit in a 512x512 square.

            sticker_format (:obj:`~pyrogram.enums.StickerFormat`):
                Format of the sticker.

        Returns:
            :obj:`~pyrogram.types.File`: The uploaded file is returned.
        """
        document = await types.InputSticker(
            sticker=sticker, format=sticker_format, emoji_list=[]
        )._upload(self, user_id)

        return types.File(
            file_id=FileId(
                file_type=FileType.STICKER,
                dc_id=document.dc_id,
                media_id=document.id,
                access_hash=document.access_hash,
                file_reference=document.file_reference,
            ).encode(),
            file_unique_id=FileUniqueId(
                file_unique_type=FileUniqueType.DOCUMENT, media_id=document.id
            ).encode(),
            file_size=document.size,
        )
