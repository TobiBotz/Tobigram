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


class GetOldFeaturedStickers:
    async def get_old_featured_stickers(
        self: pyrogram.Client,
        offset: int = 0,
        limit: int = 100,
        hash: int = 0,
    ) -> raw.base.messages.FeaturedStickers:
        """Get old featured/trending sticker sets (pagination).

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            offset (``int``, *optional*):
                Pagination offset.

            limit (``int``, *optional*):
                Maximum number of results. Defaults to 100.

            hash (``int``, *optional*):
                Hash for caching.

        Returns:
            :obj:`~pyrogram.raw.base.messages.FeaturedStickers`: The old featured sticker sets.

        Example:
            .. code-block:: python

                old_featured = await app.get_old_featured_stickers()
        """
        return await self.invoke(
            raw.functions.messages.GetOldFeaturedStickers(offset=offset, limit=limit, hash=hash)
        )
