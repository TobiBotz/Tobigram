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


class CheckDownloadFileParams:
    async def check_download_file_params(
        self: pyrogram.Client,
        bot: int | str,
        file_name: str,
        url: str,
    ) -> bool:
        """Check if a Mini App can request the download of a specific file.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            bot (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target bot.

            file_name (``str``):
                The filename from the web_app_request_file_download event.

            url (``str``):
                The URL from the web_app_request_file_download event.

        Returns:
            ``bool``: On success, True is returned.

        Example:
            .. code-block:: python

                can_download = await app.check_download_file_params("my_bot", "file.pdf", "https://example.com/file.pdf")
        """
        return await self.invoke(
            raw.functions.bots.CheckDownloadFileParams(
                bot=await self.resolve_peer(bot),
                file_name=file_name,
                url=url,
            )
        )
