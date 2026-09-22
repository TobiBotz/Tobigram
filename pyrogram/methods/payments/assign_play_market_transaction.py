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


class AssignPlayMarketTransaction:
    async def assign_play_market_transaction(
        self: pyrogram.Client,
        receipt: str | raw.base.DataJSON,
        purpose: raw.base.InputStorePaymentPurpose,
    ) -> raw.types.Updates:
        """Assign and verify a Google Play Store receipt to a payment purpose.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            receipt (``str`` | :obj:`~pyrogram.raw.base.DataJSON`):
                Google Play Store purchase JSON string or DataJSON object.

            purpose (:obj:`~pyrogram.raw.base.InputStorePaymentPurpose`):
                The store payment purpose.

        Returns:
            :obj:`~pyrogram.raw.types.Updates`: On success, updates are returned.

        Example:
            .. code-block:: python

                await app.assign_play_market_transaction(receipt_json, purpose)
        """
        receipt_obj = raw.types.DataJSON(data=receipt) if isinstance(receipt, str) else receipt

        return await self.invoke(
            raw.functions.payments.AssignPlayMarketTransaction(
                receipt=receipt_obj,
                purpose=purpose,
            )
        )
