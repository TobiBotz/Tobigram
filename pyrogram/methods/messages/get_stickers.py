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


class GetStickers:
    async def get_stickers(
        self: pyrogram.Client,
        short_name: str,
    ) -> types.StickerSet:
        """Get sticker set by short name.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            short_name (``str``):
                The short name of the sticker set.

        Returns:
            :obj:`~pyrogram.types.StickerSet`: The sticker set.

        Example:
            .. code-block:: python

                stickers = await app.get_stickers("Animals")
        """
        r = await self.invoke(
            raw.functions.messages.GetStickerSet(
                stickerset=raw.types.InputStickerSetShortName(short_name=short_name),
                hash=0,
            )
        )

        return await types.StickerSet._parse(self, r)
