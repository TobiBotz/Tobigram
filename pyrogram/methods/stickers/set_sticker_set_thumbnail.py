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
from .resolve import resolve_stickerset, resolve_thumb_doc


class SetStickerSetThumbnail:
    async def set_sticker_set_thumbnail(
        self: pyrogram.Client,
        short_name: str | types.StickerSet | raw.base.InputStickerSet,
        thumb: str | BinaryIO | raw.base.InputDocument | None = None,
    ) -> types.StickerSet:
        """Set thumbnail for a sticker set.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            short_name (``str`` | :obj:`~pyrogram.types.StickerSet`):
                Short name or StickerSet object.

            thumb (``str`` | ``BinaryIO`` | :obj:`~pyrogram.raw.base.InputDocument`, *optional*):
                Thumbnail image.

        Returns:
            :obj:`~pyrogram.types.StickerSet`: On success, the updated sticker set is returned.

        Example:
            .. code-block:: python

                await app.set_sticker_set_thumbnail("mypack", thumb="thumb.webp")
        """
        stickerset = resolve_stickerset(short_name)
        thumb_doc = await resolve_thumb_doc(self, thumb)

        r = await self.invoke(
            raw.functions.stickers.SetStickerSetThumb(
                stickerset=stickerset,
                thumb=thumb_doc,
            )
        )

        return await types.StickerSet._parse(self, r)
