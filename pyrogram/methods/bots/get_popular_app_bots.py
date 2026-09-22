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


class GetPopularAppBots:
    async def get_popular_app_bots(
        self: pyrogram.Client,
        offset: str = "",
        limit: int = 50,
    ) -> raw.base.bots.PopularAppBots:
        """Fetch popular Main Mini Apps used in global search.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            offset (``str``, *optional*):
                Offset for pagination, initially an empty string, then re-use the next_offset returned.

            limit (``int``, *optional*):
                Maximum number of results to return. Defaults to 50.

        Returns:
            :obj:`~pyrogram.raw.base.bots.PopularAppBots`: Popular Mini Apps object.

        Example:
            .. code-block:: python

                apps = await app.get_popular_app_bots()
        """
        return await self.invoke(
            raw.functions.bots.GetPopularAppBots(
                offset=offset,
                limit=limit,
            )
        )
