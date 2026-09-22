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


class GetConnectedStarRefBots:
    async def get_connected_star_ref_bots(
        self: pyrogram.Client,
        chat_id: int | str,
        limit: int = 100,
        offset_date: int | None = None,
        offset_link: str | None = None,
    ) -> raw.types.payments.ConnectedStarRefBots:
        """Get the list of connected Star affiliate referral bots for a channel.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Target channel ID.

            limit (``int``, *optional*):
                Maximum number of results to return. Defaults to 100.

            offset_date (``int``, *optional*):
                Offset date for pagination.

            offset_link (``str``, *optional*):
                Offset referral link for pagination.

        Returns:
            :obj:`~pyrogram.raw.types.payments.ConnectedStarRefBots`: Connected bots list.

        Example:
            .. code-block:: python

                bots = await app.get_connected_star_ref_bots(channel_id)
        """
        peer = await self.resolve_peer(chat_id)

        return await self.invoke(
            raw.functions.payments.GetConnectedStarRefBots(
                peer=peer,
                limit=limit,
                offset_date=offset_date,
                offset_link=offset_link,
            )
        )
