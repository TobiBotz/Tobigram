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


class GetRecentMeUrls:
    async def get_recent_me_urls(
        self: pyrogram.Client,
        referer: str = "",
    ) -> raw.base.help.RecentMeUrls:
        """Get recent t.me URLs.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            referer (``str``, *optional*):
                Referer URL. Defaults to empty string.

        Returns:
            :obj:`~pyrogram.raw.base.help.RecentMeUrls`: Recent URLs.

        Example:
            .. code-block:: python

                urls = await app.get_recent_me_urls()
        """
        return await self.invoke(
            raw.functions.help.GetRecentMeUrls(
                referer=referer,
            )
        )
