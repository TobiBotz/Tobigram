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


class ReplaceSticker:
    async def replace_sticker(
        self: pyrogram.Client,
        sticker: str | types.Sticker | raw.base.InputDocument,
        new_sticker: types.InputSticker | types.Sticker | str | BinaryIO | raw.base.InputDocument,
        *,
        emoji: str | None = None,
        keywords: str | None = None,
        mask_coords: types.MaskPosition | raw.types.MaskCoords | None = None,
    ) -> types.StickerSet:
        """Replace an existing sticker in a sticker set with a new one.

        The sticker set must have been created by the current user or bot.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            sticker (``str`` | :obj:`~pyrogram.types.Sticker` | :obj:`~pyrogram.raw.base.InputDocument`):
                The old sticker to be replaced. Pass a file_id as string, a :obj:`~pyrogram.types.Sticker` object,
                or a raw :obj:`~pyrogram.raw.base.InputDocument`.

            new_sticker (:obj:`~pyrogram.types.InputSticker` | :obj:`~pyrogram.types.Sticker` | ``str`` | ``BinaryIO`` | :obj:`~pyrogram.raw.base.InputDocument`):
                The new replacement sticker. Can be an :obj:`~pyrogram.types.InputSticker` object,
                a :obj:`~pyrogram.types.Sticker` object, a local file path, a binary file-like object,
                or a file ID.

            emoji (``str``, *optional*):
                Associated emoji for the new sticker.
                Defaults to the new sticker's emoji if available, or "😀".
                Ignored if ``new_sticker`` is an :obj:`~pyrogram.types.InputSticker`.

            keywords (``str``, *optional*):
                Search keywords separated by commas.
                Ignored if ``new_sticker`` is an :obj:`~pyrogram.types.InputSticker`.

            mask_coords (:obj:`~pyrogram.types.MaskPosition` | :obj:`~pyrogram.raw.types.MaskCoords`, *optional*):
                Mask coordinates for mask stickers.
                Ignored if ``new_sticker`` is an :obj:`~pyrogram.types.InputSticker`.

        Returns:
            :obj:`~pyrogram.types.StickerSet`: On success, the updated sticker set is returned.

        Example:
            .. code-block:: python

                # Replace an existing sticker
                await app.replace_sticker(
                    sticker=old_message.sticker,
                    new_sticker="new_sticker.webp",
                    emoji="🔥"
                )
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
