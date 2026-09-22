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


class ToggleWebBrowserSettingsException:
    async def toggle_web_browser_settings_exception(
        self: pyrogram.Client,
        url: str,
        delete: bool | None = None,
        open_external_browser: bool | None = None,
    ) -> raw.base.Updates:
        """Toggle web browser settings exception for a specific URL.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            url (``str``):
                URL to set exception for.

            delete (``bool``, *optional*):
                Whether to delete the exception.

            open_external_browser (``bool``, *optional*):
                Whether to open in external browser.

        Returns:
            :obj:`~pyrogram.raw.base.Updates`: On success, updates are returned.
        """
        return await self.invoke(
            raw.functions.account.ToggleWebBrowserSettingsException(
                url=url,
                delete=delete,
                open_external_browser=open_external_browser,
            )
        )
