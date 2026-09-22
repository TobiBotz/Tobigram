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


class UpdateTheme:
    async def update_theme(
        self: pyrogram.Client,
        format: str,
        theme: raw.base.InputTheme,
        slug: str | None = None,
        title: str | None = None,
        document: raw.base.InputDocument | None = None,
        settings: list[raw.base.InputThemeSettings] | None = None,
    ) -> raw.base.Theme:
        """Update a theme.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            format (``str``):
                Theme format, a string that identifies the theming engines supported by the client.

            theme (:obj:`~pyrogram.raw.base.InputTheme`):
                Theme to update.

            slug (``str``, *optional*):
                Unique theme ID.

            title (``str``, *optional*):
                Theme name.

            document (:obj:`~pyrogram.raw.base.InputDocument`, *optional*):
                Theme file.

            settings (List of :obj:`~pyrogram.raw.base.InputThemeSettings`, *optional*):
                Theme settings.

        Returns:
            :obj:`~pyrogram.raw.base.Theme`: On success, the updated theme is returned.
        """
        return await self.invoke(
            raw.functions.account.UpdateTheme(
                format=format,
                theme=theme,
                slug=slug,
                title=title,
                document=document,
                settings=settings,
            )
        )
