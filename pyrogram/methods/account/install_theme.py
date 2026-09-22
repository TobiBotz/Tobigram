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


class InstallTheme:
    async def install_theme(
        self: pyrogram.Client,
        dark: bool | None = None,
        theme: raw.base.InputTheme | None = None,
        format: str | None = None,
        base_theme: raw.base.BaseTheme | None = None,
    ) -> bool:
        """Install a theme.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            dark (``bool``, *optional*):
                Whether to install the dark version.

            theme (:obj:`~pyrogram.raw.base.InputTheme`, *optional*):
                Theme to install.

            format (``str``, *optional*):
                Theme format, a string that identifies the theming engines supported by the client.

            base_theme (:obj:`~pyrogram.raw.base.BaseTheme`, *optional*):
                Indicates a basic theme provided by all clients.

        Returns:
            ``bool``: On success, True is returned.
        """
        return await self.invoke(
            raw.functions.account.InstallTheme(
                dark=dark,
                theme=theme,
                format=format,
                base_theme=base_theme,
            )
        )
