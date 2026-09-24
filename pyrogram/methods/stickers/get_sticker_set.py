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


class GetStickerSet:
    async def get_sticker_set(self: pyrogram.Client, name: str) -> types.StickerSet:
        """Get a sticker set by its name.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            name (``str``):
                Name of the sticker set.

        Returns:
            :obj:`~pyrogram.types.StickerSet`: The sticker set is returned.

        Example:
            .. code-block:: python

                await app.get_sticker_set("animals")
        """
        r = await self.invoke(
            raw.functions.messages.GetStickerSet(
                stickerset=raw.types.InputStickerSetShortName(short_name=name), hash=0
            )
        )

        return await types.StickerSet._parse(self, r)
