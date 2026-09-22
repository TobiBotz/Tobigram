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


class GetPremiumGiftCodeOptions:
    async def get_premium_gift_code_options(
        self: pyrogram.Client,
        boost_chat_id: int | str | None = None,
    ) -> list[raw.types.PremiumGiftCodeOption]:
        """Get Telegram Premium gift code options and pricing.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            boost_chat_id (``int`` | ``str``, *optional*):
                Channel to boost with the gift code purchase.

        Returns:
            List of :obj:`~pyrogram.raw.types.PremiumGiftCodeOption`: Available options.

        Example:
            .. code-block:: python

                options = await app.get_premium_gift_code_options(channel_id)
        """
        peer = await self.resolve_peer(boost_chat_id) if boost_chat_id else None

        return await self.invoke(
            raw.functions.payments.GetPremiumGiftCodeOptions(
                boost_peer=peer,
            )
        )
