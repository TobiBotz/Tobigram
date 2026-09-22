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

import pyrogram
from pyrogram import raw, types
from .resolve import resolve_sticker_doc


class ChangeStickerSet:
    async def change_sticker_set(
        self: pyrogram.Client,
        sticker: str | types.Sticker | raw.base.InputDocument,
        *,
        emoji: str | None = None,
        keywords: str | None = None,
        mask_coords: types.MaskPosition | raw.types.MaskCoords | None = None,
    ) -> types.StickerSet:
        """Update the emoji list, search keywords, or mask coordinates of an existing sticker.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            sticker (``str`` | :obj:`~pyrogram.types.Sticker` | :obj:`~pyrogram.raw.base.InputDocument`):
                The sticker to update.

            emoji (``str``, *optional*):
                If set, updates the emoji list associated with the sticker.

            keywords (``str``, *optional*):
                If set, updates the sticker search keywords.

            mask_coords (:obj:`~pyrogram.types.MaskPosition` | :obj:`~pyrogram.raw.types.MaskCoords`, *optional*):
                If set, updates the mask coordinates for mask stickers.

        Returns:
            :obj:`~pyrogram.types.StickerSet`: On success, the updated sticker set is returned.

        Example:
            .. code-block:: python

                await app.change_sticker_set(
                    sticker=message.sticker,
                    emoji="🎉🥳",
                )
        """
        doc = await resolve_sticker_doc(self, sticker)

        if isinstance(mask_coords, types.MaskPosition):
            point_val = (
                mask_coords.point.value
                if hasattr(mask_coords.point, "value")
                else int(mask_coords.point)
            )
            mask_coords = raw.types.MaskCoords(
                n=point_val,
                x=mask_coords.x_shift,
                y=mask_coords.y_shift,
                zoom=mask_coords.scale,
            )

        r = await self.invoke(
            raw.functions.stickers.ChangeSticker(
                sticker=doc,
                emoji=emoji,
                keywords=keywords,
                mask_coords=mask_coords,
            )
        )

        return await types.StickerSet._parse(self, r)
