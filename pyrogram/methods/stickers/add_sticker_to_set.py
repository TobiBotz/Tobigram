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
from .resolve import resolve_sticker_item, resolve_stickerset


class AddStickerToSet:
    async def add_sticker_to_set(
        self: pyrogram.Client,
        short_name: str | types.StickerSet | raw.base.InputStickerSet,
        sticker: types.InputSticker | types.Sticker | str | BinaryIO | raw.base.InputDocument,
        *,
        emoji: str | None = None,
        keywords: str | None = None,
        mask_coords: raw.types.MaskCoords | None = None,
    ) -> types.StickerSet:
        """Add a sticker to an existing sticker set created by you or your bot.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            short_name (``str`` | :obj:`~pyrogram.types.StickerSet`):
                Short name or StickerSet object of the target sticker set.

            sticker (:obj:`~pyrogram.types.InputSticker` | ``str`` | ``BinaryIO`` | :obj:`~pyrogram.raw.base.InputDocument`):
                The sticker to add. Can be an :obj:`~pyrogram.types.InputSticker` object,
                a file path string, a binary file-like object, or a file ID.

            emoji (``str``, *optional*):
                Associated emoji for the sticker.
                Ignored if ``sticker`` is an :obj:`~pyrogram.types.InputSticker`.
                Defaults to "😀".

            keywords (``str``, *optional*):
                Keywords separated by commas.
                Ignored if ``sticker`` is an :obj:`~pyrogram.types.InputSticker`.

            mask_coords (:obj:`~pyrogram.raw.types.MaskCoords`, *optional*):
                Mask coordinates for mask stickers.
                Ignored if ``sticker`` is an :obj:`~pyrogram.types.InputSticker`.

        Returns:
            :obj:`~pyrogram.types.StickerSet`: On success, the updated sticker set is returned.

        Example:
            .. code-block:: python

                # Add a sticker with emoji
                await app.add_sticker_to_set(
                    short_name="mypack_by_bot",
                    sticker="sticker3.webp",
                    emoji="🚀"
                )

                # Add an InputSticker
                await app.add_sticker_to_set(
                    short_name="mypack_by_bot",
                    sticker=types.InputSticker("sticker3.webp", emoji="🚀", keywords="rocket, space")
                )
        """
        stickerset = resolve_stickerset(short_name)

        if isinstance(sticker, types.InputSticker):
            item = await resolve_sticker_item(self, sticker)
        else:
            input_stk = types.InputSticker(
                sticker=sticker,
                emoji=emoji,
                keywords=keywords,
                mask_coords=mask_coords,
            )
            item = await resolve_sticker_item(self, input_stk)

        r = await self.invoke(
            raw.functions.stickers.AddStickerToSet(
                stickerset=stickerset,
                sticker=item,
            )
        )

        return await types.StickerSet._parse(self, r)
