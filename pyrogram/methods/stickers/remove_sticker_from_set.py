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


class RemoveStickerFromSet:
    async def remove_sticker_from_set(
        self: pyrogram.Client,
        sticker: str | types.Sticker | raw.base.InputDocument,
    ) -> types.StickerSet:
        """Remove a sticker from the set where it belongs.

        The sticker set must have been created by the current user or bot.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            sticker (``str`` | :obj:`~pyrogram.types.Sticker` | :obj:`~pyrogram.raw.base.InputDocument`):
                The sticker to remove. Can be a sticker's ``file_id``, a :obj:`~pyrogram.types.Sticker`
                object, or a raw :obj:`~pyrogram.raw.base.InputDocument`.

        Returns:
            :obj:`~pyrogram.types.StickerSet`: On success, the updated sticker set is returned.

        Example:
            .. code-block:: python

                # Remove a sticker by file_id
                await app.remove_sticker_from_set("CAACAgIAAxkBAAE...")

                # Remove using a Sticker object
                await app.remove_sticker_from_set(sticker_obj)
        """
        doc = await resolve_sticker_doc(self, sticker)

        r = await self.invoke(
            raw.functions.stickers.RemoveStickerFromSet(
                sticker=doc,
            )
        )

        return await types.StickerSet._parse(self, r)
