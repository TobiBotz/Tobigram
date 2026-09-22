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


class GetWallPaper:
    async def get_wall_paper(
        self: pyrogram.Client,
        wallpaper: raw.base.InputWallPaper,
    ) -> raw.base.WallPaper:
        """Get info about a certain wallpaper.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            wallpaper (:obj:`~pyrogram.raw.base.InputWallPaper`):
                The wallpaper to get info about.

        Returns:
            :obj:`~pyrogram.raw.base.WallPaper`: On success, the wallpaper is returned.
        """
        return await self.invoke(
            raw.functions.account.GetWallPaper(
                wallpaper=wallpaper,
            )
        )
