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
from pyrogram import raw, types


class GetStarsRevenueStats:
    async def get_stars_revenue_stats(
        self: pyrogram.Client,
        chat_id: int | str | None = None,
        dark: bool = False,
        ton: bool = False,
    ) -> types.StarsRevenueStats:
        """Get Telegram Stars revenue statistics and monetization status for a channel or bot.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            chat_id (``int`` | ``str``, *optional*):
                Unique identifier (int) or username (str) of the target channel or bot.
                Defaults to None (the current account / "me").

            dark (``bool``, *optional*):
                Pass True if the revenue graph should be styled for dark theme.
                Defaults to False.

            ton (``bool``, *optional*):
                Pass True to retrieve TON revenue statistics instead of Stars.
                Defaults to False.

        Returns:
            :obj:`~pyrogram.types.StarsRevenueStats`: On success, the stars revenue stats object is returned.

        Example:
            .. code-block:: python

                # Get revenue stats for a channel
                stats = await app.get_stars_revenue_stats(chat_id="my_channel")
                print(f"Current Balance: {stats.status.current_balance} Stars")
                print(f"Available Balance: {stats.status.available_balance} Stars")
                print(f"Overall Revenue: {stats.status.overall_revenue} Stars")
                print(f"USD Exchange Rate: ${stats.usd_rate} per star")
                print(f"Withdrawal Enabled: {stats.status.withdrawal_enabled}")
        """
        if chat_id is None:
            peer = raw.types.InputPeerSelf()
        else:
            peer = await self.resolve_peer(chat_id)

        r = await self.invoke(
            raw.functions.payments.GetStarsRevenueStats(
                peer=peer,
                dark=dark or None,
                ton=ton or None,
            )
        )

        return types.StarsRevenueStats._parse(self, r)
