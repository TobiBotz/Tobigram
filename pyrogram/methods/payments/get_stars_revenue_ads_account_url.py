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


class GetStarsRevenueAdsAccountUrl:
    async def get_stars_revenue_ads_account_url(
        self: pyrogram.Client,
        chat_id: int | str,
    ) -> str:
        """Get the URL of the Telegram Ads account for stars revenue.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Target chat ID (bot or channel).

        Returns:
            ``str``: On success, URL string is returned.

        Example:
            .. code-block:: python

                url = await app.get_stars_revenue_ads_account_url(channel_id)
        """
        peer = await self.resolve_peer(chat_id)

        r = await self.invoke(
            raw.functions.payments.GetStarsRevenueAdsAccountUrl(
                peer=peer,
            )
        )

        return r.url
