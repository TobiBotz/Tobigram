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


class GetStarGiftAuctionAcquiredGifts:
    async def get_star_gift_auction_acquired_gifts(
        self: pyrogram.Client,
        gift_id: int,
    ) -> raw.types.payments.StarGiftAuctionAcquiredGifts:
        """Get the list of gifts acquired in a specific Star Gift auction.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            gift_id (``int``):
                The gift identifier.

        Returns:
            :obj:`~pyrogram.raw.types.payments.StarGiftAuctionAcquiredGifts`: Acquired gifts object.

        Example:
            .. code-block:: python

                gifts = await app.get_star_gift_auction_acquired_gifts(gift_id)
        """
        return await self.invoke(
            raw.functions.payments.GetStarGiftAuctionAcquiredGifts(
                gift_id=gift_id,
            )
        )
