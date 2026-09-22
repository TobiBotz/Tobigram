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


class CanPurchaseStore:
    async def can_purchase_store(
        self: pyrogram.Client,
        purpose: raw.base.InputStorePaymentPurpose,
    ) -> bool:
        """Check if an in-app store purchase can be made for the given purpose.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            purpose (:obj:`~pyrogram.raw.base.InputStorePaymentPurpose`):
                The payment purpose.

        Returns:
            ``bool``: True if store purchase is allowed, False otherwise.

        Example:
            .. code-block:: python

                can_buy = await app.can_purchase_store(purpose)
        """
        return await self.invoke(
            raw.functions.payments.CanPurchaseStore(
                purpose=purpose,
            )
        )
