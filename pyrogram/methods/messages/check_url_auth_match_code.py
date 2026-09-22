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


class CheckUrlAuthMatchCode:
    async def check_url_auth_match_code(
        self: pyrogram.Client,
        url: str,
        match_code: str,
    ) -> raw.base.UrlAuthResult:
        """Check a URL auth match code.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            url (``str``):
                The URL to check.

            match_code (``str``):
                The match code to verify.

        Returns:
            :obj:`~pyrogram.raw.base.UrlAuthResult`: The URL auth result.

        Example:
            .. code-block:: python

                result = await app.check_url_auth_match_code("https://example.com", "code123")
        """
        return await self.invoke(
            raw.functions.messages.CheckUrlAuthMatchCode(url=url, match_code=match_code)
        )
