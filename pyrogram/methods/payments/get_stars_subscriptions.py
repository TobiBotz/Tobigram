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


class GetStarsSubscriptions:
    async def get_stars_subscriptions(
        self: pyrogram.Client,
        chat_id: int | str = "me",
        offset: str = "",
        missing_balance: bool | None = None,
    ) -> raw.types.payments.StarsStatus:
        """Get Telegram Stars subscriptions of a user or channel.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``, *optional*):
                Unique identifier of the target chat or "me". Defaults to "me".

            offset (``str``, *optional*):
                Offset for pagination. Defaults to "".

            missing_balance (``bool``, *optional*):
                Filter by missing balance.

        Returns:
            :obj:`~pyrogram.raw.types.payments.StarsStatus`: On success, stars status is returned.

        Example:
            .. code-block:: python

                subs = await app.get_stars_subscriptions()
        """
        peer = await self.resolve_peer(chat_id)

        return await self.invoke(
            raw.functions.payments.GetStarsSubscriptions(
                peer=peer,
                offset=offset,
                missing_balance=missing_balance,
            )
        )
