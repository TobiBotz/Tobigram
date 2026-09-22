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
from .resolve import resolve_sticker_doc, resolve_sticker_item


class ReplaceStickerInSet:
    async def replace_sticker_in_set(
        self: pyrogram.Client,
        sticker: str | types.Sticker | raw.base.InputDocument,
        new_sticker: types.InputSticker | str | BinaryIO | raw.base.InputDocument,
        *,
        emoji: str | None = None,
        keywords: str | None = None,
        mask_coords: raw.types.MaskCoords | None = None,
    ) -> types.StickerSet:
        """Replace a sticker in a sticker set.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            sticker (``str`` | :obj:`~pyrogram.types.Sticker` | :obj:`~pyrogram.raw.base.InputDocument`):
                Old sticker to replace.

            new_sticker (:obj:`~pyrogram.types.InputSticker` | ``str`` | ``BinaryIO`` | :obj:`~pyrogram.raw.base.InputDocument`):
                New sticker to replace with.

            emoji (``str``, *optional*):
                Emoji associated with new sticker.

            keywords (``str``, *optional*):
                Keywords separated by commas.

            mask_coords (:obj:`~pyrogram.raw.types.MaskCoords`, *optional*):
                Mask coordinates.

        Returns:
            :obj:`~pyrogram.types.StickerSet`: On success, the updated sticker set is returned.

        Example:
            .. code-block:: python

                await app.replace_sticker_in_set(old_sticker, "new_sticker.webp")
        """
        old_doc = await resolve_sticker_doc(self, sticker)

        if isinstance(new_sticker, types.InputSticker):
            item = await resolve_sticker_item(self, new_sticker)
        else:
            input_stk = types.InputSticker(
                sticker=new_sticker,
                emoji=emoji,
                keywords=keywords,
                mask_coords=mask_coords,
            )
            item = await resolve_sticker_item(self, input_stk)

        r = await self.invoke(
            raw.functions.stickers.ReplaceSticker(
                sticker=old_doc,
                new_sticker=item,
            )
        )

        return await types.StickerSet._parse(self, r)
