#  Pyrogram - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-present Dan <https://github.com/delivrance>
#
#  This file is part of Pyrogram.
#
#  Pyrogram is free software: you can redistribute it dand/or modify
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
from .resolve import resolve_stickerset, resolve_thumb_doc


class SetStickerSetThumb:
    async def set_sticker_set_thumb(
        self: pyrogram.Client,
        short_name: str | types.StickerSet | raw.base.InputStickerSet,
        *,
        thumb: str | BinaryIO | raw.base.InputDocument | None = None,
        thumb_document_id: int = 0,
    ) -> types.StickerSet:
        """Set thumbnail for a sticker set created by you or your bot.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            short_name (``str`` | :obj:`~pyrogram.types.StickerSet`):
                Short name or StickerSet object of the sticker set.

            thumb (``str`` | ``BinaryIO`` | :obj:`~pyrogram.raw.base.InputDocument`, *optional*):
                Thumbnail file for normal sticker sets. Can be a local file path, a file-like object,
                or a raw InputDocument.

            thumb_document_id (``int``, *optional*):
                Only for custom emoji sticker sets: document ID of a custom emoji in the set to use as thumbnail.
                Pass 0 to fallback to the first custom emoji.

        Returns:
            :obj:`~pyrogram.types.StickerSet`: On success, the updated sticker set is returned.

        Example:
            .. code-block:: python

                # Set sticker set thumbnail
                await app.set_sticker_set_thumb("mypack_by_bot", thumb="thumb.webp")
        """
        stickerset = resolve_stickerset(short_name)
        thumb_doc = await resolve_thumb_doc(self, thumb)

        r = await self.invoke(
            raw.functions.stickers.SetStickerSetThumb(
                stickerset=stickerset,
                thumb=thumb_doc,
                thumb_document_id=thumb_document_id or None,
            )
        )

        return await types.StickerSet._parse(self, r)
