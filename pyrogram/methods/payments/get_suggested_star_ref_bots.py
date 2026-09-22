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


class GetSuggestedStarRefBots:
    async def get_suggested_star_ref_bots(
        self: pyrogram.Client,
        chat_id: int | str,
        offset: str = "",
        limit: int = 100,
        order_by_revenue: bool | None = None,
        order_by_date: bool | None = None,
    ) -> raw.types.payments.SuggestedStarRefBots:
        """Get suggested Star affiliate referral bots for a channel.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Target channel ID.

            offset (``str``, *optional*):
                Offset string for pagination. Defaults to "".

            limit (``int``, *optional*):
                Maximum number of bots to return. Defaults to 100.

            order_by_revenue (``bool``, *optional*):
                Sort results by revenue.

            order_by_date (``bool``, *optional*):
                Sort results by connection date.

        Returns:
            :obj:`~pyrogram.raw.types.payments.SuggestedStarRefBots`: Suggested bots list.

        Example:
            .. code-block:: python

                bots = await app.get_suggested_star_ref_bots(channel_id)
        """
        peer = await self.resolve_peer(chat_id)

        return await self.invoke(
            raw.functions.payments.GetSuggestedStarRefBots(
                peer=peer,
                offset=offset,
                limit=limit,
                order_by_revenue=order_by_revenue,
                order_by_date=order_by_date,
            )
        )
