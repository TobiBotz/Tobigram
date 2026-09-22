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


class GetWebPage:
    async def get_web_page(
        self: pyrogram.Client,
        url: str,
        hash: int = 0,
    ) -> raw.base.WebPage:
        """Get information about a web page via URL.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            url (``str``):
                The URL of the web page.

            hash (``int``, *optional*):
                Hash for caching, for more info click :here:`here`.

        Returns:
            :obj:`~pyrogram.raw.base.WebPage`: The web page information.

        Example:
            .. code-block:: python

                page = await app.get_web_page("https://example.com")
        """
        return await self.invoke(raw.functions.messages.GetWebPage(url=url, hash=hash))
