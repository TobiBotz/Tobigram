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
from .resolve import resolve_stickerset


class GetStickerSet:
    async def get_sticker_set(
        self: pyrogram.Client,
        short_name: str | types.StickerSet | raw.base.InputStickerSet,
    ) -> types.StickerSet:
        """Get information about a sticker set, including all its stickers.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            short_name (``str`` | :obj:`~pyrogram.types.StickerSet`):
                Short name or StickerSet object of the sticker set.

        Returns:
            :obj:`~pyrogram.types.StickerSet`: On success, the sticker set is returned.

        Example:
            .. code-block:: python

                # Get a sticker set by short name
                sticker_set = await app.get_sticker_set("Animals")
                print(sticker_set.title)
                print(len(sticker_set.stickers))
        """
        stickerset = resolve_stickerset(short_name)

        r = await self.invoke(
            raw.functions.messages.GetStickerSet(
                stickerset=stickerset,
                hash=0,
            )
        )

        return await types.StickerSet._parse(self, r)
