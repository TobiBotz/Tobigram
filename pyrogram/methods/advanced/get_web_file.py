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


class GetWebFile:
    async def get_web_file(
        self: pyrogram.Client,
        location: raw.base.InputWebFileLocation,
        offset: int = 0,
        limit: int = 1048576,
    ) -> raw.base.upload.WebFile:
        """Returns content of a web file, by proxying the request through Telegram.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            location (:obj:`~pyrogram.raw.base.InputWebFileLocation`):
                The web file to download.

            offset (``int``, *optional*):
                Number of bytes to be skipped. Defaults to 0.

            limit (``int``, *optional*):
                Number of bytes to be returned. Defaults to 1048576 (1MB).

        Returns:
            :obj:`~pyrogram.raw.base.upload.WebFile`: The downloaded web file data.

        Example:
            .. code-block:: python

                web_file = await app.get_web_file(location)
        """
        return await self.invoke(
            raw.functions.upload.GetWebFile(
                location=location,
                offset=offset,
                limit=limit,
            )
        )
