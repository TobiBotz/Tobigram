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


class SaveAutoDownloadSettings:
    async def save_auto_download_settings(
        self: pyrogram.Client,
        settings: raw.base.AutoDownloadSettings,
        low: bool | None = None,
        high: bool | None = None,
    ) -> bool:
        """Change media autodownload settings.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            settings (:obj:`~pyrogram.raw.base.AutoDownloadSettings`):
                Media autodownload settings.

            low (``bool``, *optional*):
                Whether to save media in the low data usage preset.

            high (``bool``, *optional*):
                Whether to save media in the high data usage preset.

        Returns:
            ``bool``: On success, True is returned.
        """
        return await self.invoke(
            raw.functions.account.SaveAutoDownloadSettings(
                settings=settings,
                low=low,
                high=high,
            )
        )
