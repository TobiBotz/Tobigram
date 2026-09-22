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


class GetDeepLinkInfo:
    async def get_deep_link_info(
        self: pyrogram.Client,
        path: str,
    ) -> raw.base.help.DeepLinkInfo:
        """Get info about an unsupported deep link.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            path (``str``):
                The path of the deep link.

        Returns:
            :obj:`~pyrogram.raw.base.help.DeepLinkInfo`: The deep link info.

        Example:
            .. code-block:: python

                info = await app.get_deep_link_info("path")
        """
        return await self.invoke(
            raw.functions.help.GetDeepLinkInfo(
                path=path,
            )
        )
