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

from collections.abc import AsyncGenerator

import pyrogram
from pyrogram import raw, types


class GetOwnedStickerSets:
    async def get_owned_sticker_sets(
        self: pyrogram.Client,
        limit: int = 0,
        offset_id: int = 0,
    ) -> AsyncGenerator[types.StickerSet, None]:
        """Get your owned sticker sets.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            limit (``int``, *optional*):
                Limits the number of sticker sets to be retrieved.
                By default, no limit is applied and all sticker sets are returned.

            offset_id (``int``, *optional*):
                Offset ID for pagination.

        Returns:
            ``AsyncGenerator``: Yields :obj:`~pyrogram.types.StickerSet` objects.

        Example:
            .. code-block:: python

                async for sticker_set in app.get_owned_sticker_sets():
                    print(sticker_set.title)
        """
        current = 0
        total = limit or (1 << 31) - 1

        while True:
            r = await self.invoke(
                raw.functions.messages.GetMyStickers(
                    offset_id=offset_id,
                    limit=min(total - current, 100),
                )
            )

            if not r.sets:
                break

            for set_covered in r.sets:
                yield await types.StickerSet._parse(self, set_covered)

                current += 1
                if current >= total:
                    return

            offset_id = r.sets[-1].set.id
