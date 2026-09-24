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
        self: pyrogram.Client, limit: int = 0, offset_sticker_set_id: int = 0
    ) -> AsyncGenerator[types.StickerSet, None]:
        """Get the sticker sets owned by the current user.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            limit (``int``, *optional*):
                Limits the number of sticker sets to be retrieved.
                By default, no limit is applied and all sets are returned.

            offset_sticker_set_id (``int``, *optional*):
                Identifier of the sticker set from which to return owned sticker sets.

        Returns:
            ``Generator``: A generator yielding :obj:`~pyrogram.types.StickerSet` objects.

        Example:
            .. code-block:: python

                async for sticker_set in app.get_owned_sticker_sets():
                    print(sticker_set)
        """
        seen = set()
        total = limit or (1 << 31) - 1
        limit = min(100, total)

        while True:
            r = await self.invoke(
                raw.functions.messages.GetMyStickers(offset_id=offset_sticker_set_id, limit=limit)
            )

            new_sets = [covered.set for covered in r.sets if covered.set.id not in seen]

            if not new_sets:
                return

            for raw_set in new_sets:
                seen.add(raw_set.id)
                offset_sticker_set_id = raw_set.id

                yield await types.StickerSet._parse(self, raw_set)

                if len(seen) >= total:
                    return

            if len(r.sets) < limit or len(seen) >= r.count:
                return
