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


class SetStickerKeywords:
    async def set_sticker_keywords(
        self: pyrogram.Client,
        sticker: str | types.Sticker | raw.base.InputDocument,
        keywords: str,
    ) -> types.StickerSet:
        """Set search keywords for a sticker.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            sticker (``str`` | :obj:`~pyrogram.types.Sticker` | :obj:`~pyrogram.raw.base.InputDocument`):
                The sticker to update.

            keywords (``str``):
                Keywords separated by commas.

        Returns:
            :obj:`~pyrogram.types.StickerSet`: On success, the updated sticker set is returned.

        Example:
            .. code-block:: python

                await app.set_sticker_keywords(sticker, "party, celebrate")
        """
        doc = await resolve_sticker_doc(self, sticker)

        r = await self.invoke(
            raw.functions.stickers.ChangeSticker(
                sticker=doc,
                keywords=keywords,
            )
        )

        return await types.StickerSet._parse(self, r)
