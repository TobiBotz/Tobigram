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


class GetStarsRevenueWithdrawalUrl:
    async def get_stars_revenue_withdrawal_url(
        self: pyrogram.Client,
        chat_id: int | str,
        password: str | raw.base.InputCheckPasswordSRP,
        ton: bool | None = None,
        amount: int | None = None,
    ) -> raw.types.payments.StarsRevenueWithdrawalUrl:
        """Get the Fragment withdrawal URL for Telegram Stars revenue.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Target chat ID (bot or channel) or "me".

            password (``str`` | :obj:`~pyrogram.raw.base.InputCheckPasswordSRP`):
                Two-step verification 2FA password.

            ton (``bool``, *optional*):
                Whether to withdraw in TON.

            amount (``int``, *optional*):
                Amount of Stars to withdraw.

        Returns:
            :obj:`~pyrogram.raw.types.payments.StarsRevenueWithdrawalUrl`: On success, withdrawal URL is returned.

        Example:
            .. code-block:: python

                url = await app.get_stars_revenue_withdrawal_url(chat_id, "2fa_password")
        """
        peer = await self.resolve_peer(chat_id)
        pwd = await self.check_password(password) if isinstance(password, str) else password

        return await self.invoke(
            raw.functions.payments.GetStarsRevenueWithdrawalUrl(
                peer=peer,
                password=pwd,
                ton=ton,
                amount=amount,
            )
        )
