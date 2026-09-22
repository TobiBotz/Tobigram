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


class GetPaymentReceipt:
    async def get_payment_receipt(
        self: pyrogram.Client,
        chat_id: int | str,
        message_id: int,
    ) -> raw.types.payments.PaymentReceipt:
        """Get payment receipt for a successful payment message.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Target chat ID where the invoice/receipt message is located.

            message_id (``int``):
                Message identifier of the payment.

        Returns:
            :obj:`~pyrogram.raw.types.payments.PaymentReceipt`: Payment receipt object.

        Example:
            .. code-block:: python

                receipt = await app.get_payment_receipt(chat_id, 123)
        """
        peer = await self.resolve_peer(chat_id)

        return await self.invoke(
            raw.functions.payments.GetPaymentReceipt(
                peer=peer,
                msg_id=message_id,
            )
        )
