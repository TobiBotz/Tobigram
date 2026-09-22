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


class GetMegagroupStats:
    async def get_megagroup_stats(
        self: pyrogram.Client,
        chat_id: int | str,
        dark: bool | None = None,
    ) -> raw.base.stats.MegagroupStats:
        """Get supergroup statistics.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target supergroup.

            dark (``bool``, *optional*):
                Whether to enable dark theme for graph colors.

        Returns:
            :obj:`~pyrogram.raw.base.stats.MegagroupStats`: The megagroup statistics.

        Example:
            .. code-block:: python

                stats = await app.get_megagroup_stats(chat_id)
        """
        return await self.invoke(
            raw.functions.stats.GetMegagroupStats(
                channel=await self.resolve_peer(chat_id),
                dark=dark,
            )
        )
