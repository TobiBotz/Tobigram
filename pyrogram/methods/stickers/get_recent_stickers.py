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


class GetRecentStickers:
    async def get_recent_stickers(
        self: pyrogram.Client, is_attached: bool | None = None
    ) -> list[types.Sticker]:
        """Get the list of recently used stickers.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            is_attached (``bool``, *optional*):
                Pass True to target the list of stickers recently attached to photo or video files.
                Pass False to target the list of recently sent stickers.

        Returns:
            List of :obj:`~pyrogram.types.Sticker`: On success, a list of sticker objects is returned.

        Example:
            .. code-block:: python

                await app.get_recent_stickers()
        """
        r = await self.invoke(
            raw.functions.messages.GetRecentStickers(hash=0, attached=is_attached)
        )

        return types.List(
            [
                await types.Sticker._parse(self, sticker, {type(a): a for a in sticker.attributes})
                for sticker in getattr(r, "stickers", [])
                if isinstance(sticker, raw.types.Document)
            ]
        )
