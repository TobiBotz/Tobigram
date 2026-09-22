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


class CreateTheme:
    async def create_theme(
        self: pyrogram.Client,
        slug: str,
        title: str,
        document: raw.base.InputDocument | None = None,
        settings: list[raw.base.InputThemeSettings] | None = None,
    ) -> raw.base.Theme:
        """Create a theme.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            slug (``str``):
                Unique theme ID used to generate theme deep links, can be empty to autogenerate a random ID.

            title (``str``):
                Theme name.

            document (:obj:`~pyrogram.raw.base.InputDocument`, *optional*):
                Theme file.

            settings (List of :obj:`~pyrogram.raw.base.InputThemeSettings`, *optional*):
                Theme settings, multiple values can be provided for the different base themes (day/night mode, etc).

        Returns:
            :obj:`~pyrogram.raw.base.Theme`: On success, the created theme is returned.
        """
        return await self.invoke(
            raw.functions.account.CreateTheme(
                slug=slug,
                title=title,
                document=document,
                settings=settings,
            )
        )
