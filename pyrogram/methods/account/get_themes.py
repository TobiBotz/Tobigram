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


class GetThemes:
    async def get_themes(
        self: pyrogram.Client,
        format: str,
        hash: int = 0,
    ) -> raw.base.account.Themes:
        """Get installed themes.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            format (``str``):
                Theme format, a string that identifies the theming engines supported by the client.

            hash (``int``, *optional*):
                Hash used for caching, defaults to 0.

        Returns:
            :obj:`~pyrogram.raw.base.account.Themes`: On success, the themes are returned.
        """
        return await self.invoke(
            raw.functions.account.GetThemes(
                format=format,
                hash=hash,
            )
        )
