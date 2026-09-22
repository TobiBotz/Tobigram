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


class ValidateRequestedInfo:
    async def validate_requested_info(
        self: pyrogram.Client,
        invoice: raw.base.InputInvoice,
        info: raw.base.PaymentRequestedInfo,
        save: bool | None = None,
    ) -> raw.types.payments.ValidatedRequestedInfo:
        """Validate requested order and shipping information before payment.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            invoice (:obj:`~pyrogram.raw.base.InputInvoice`):
                The invoice.

            info (:obj:`~pyrogram.raw.base.PaymentRequestedInfo`):
                Order and shipping information.

            save (``bool``, *optional*):
                Whether to save the information for future purchases.

        Returns:
            :obj:`~pyrogram.raw.types.payments.ValidatedRequestedInfo`: Validated info.

        Example:
            .. code-block:: python

                res = await app.validate_requested_info(invoice, info, save=True)
        """
        return await self.invoke(
            raw.functions.payments.ValidateRequestedInfo(
                invoice=invoice,
                info=info,
                save=save,
            )
        )
