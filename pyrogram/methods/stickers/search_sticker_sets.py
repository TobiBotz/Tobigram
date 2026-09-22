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
from pyrogram import raw


class SearchStickerSets:
    async def search_sticker_sets(
        self: pyrogram.Client,
        query: str,
        exclude_featured: bool = False,
        hash: int = 0,
    ) -> raw.base.messages.FoundStickerSets:
        """Search for sticker sets.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            query (``str``):
                Query string.

            exclude_featured (``bool``, *optional*):
                Pass True to exclude featured sticker sets.

            hash (``int``, *optional*):
                Hash for caching.

        Returns:
            :obj:`~pyrogram.raw.base.messages.FoundStickerSets`: Found sticker sets object.

        Example:
            .. code-block:: python

                sets = await app.search_sticker_sets("cats")
        """
        return await self.invoke(
            raw.functions.messages.SearchStickerSets(
                q=query,
                exclude_featured=exclude_featured or None,
                hash=hash,
            )
        )
