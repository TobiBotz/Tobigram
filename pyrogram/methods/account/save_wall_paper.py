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


class SaveWallPaper:
    async def save_wall_paper(
        self: pyrogram.Client,
        wallpaper: raw.base.InputWallPaper,
        unsave: bool,
        settings: raw.base.WallPaperSettings,
    ) -> bool:
        """Install or uninstall wallpaper.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            wallpaper (:obj:`~pyrogram.raw.base.InputWallPaper`):
                Wallpaper to install or uninstall.

            unsave (``bool``):
                Uninstall wallpaper?

            settings (:obj:`~pyrogram.raw.base.WallPaperSettings`):
                Wallpaper settings.

        Returns:
            ``bool``: On success, True is returned.
        """
        return await self.invoke(
            raw.functions.account.SaveWallPaper(
                wallpaper=wallpaper,
                unsave=unsave,
                settings=settings,
            )
        )
