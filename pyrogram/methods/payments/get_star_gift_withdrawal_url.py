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


class GetStarGiftWithdrawalUrl:
    async def get_star_gift_withdrawal_url(
        self: pyrogram.Client,
        stargift: raw.base.InputSavedStarGift,
        password: str | raw.base.InputCheckPasswordSRP,
    ) -> str:
        """Get the blockchain/Fragment withdrawal URL to transfer an upgraded Star Gift.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            stargift (:obj:`~pyrogram.raw.base.InputSavedStarGift`):
                The input saved star gift to withdraw.

            password (``str`` | :obj:`~pyrogram.raw.base.InputCheckPasswordSRP`):
                Two-step verification 2FA password.

        Returns:
            ``str``: On success, the withdrawal URL is returned.

        Example:
            .. code-block:: python

                url = await app.get_star_gift_withdrawal_url(stargift, "2fa_password")
        """
        pwd = await self.check_password(password) if isinstance(password, str) else password

        r = await self.invoke(
            raw.functions.payments.GetStarGiftWithdrawalUrl(
                stargift=stargift,
                password=pwd,
            )
        )

        return r.url
