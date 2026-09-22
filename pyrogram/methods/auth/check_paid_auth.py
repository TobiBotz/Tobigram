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


class CheckPaidAuth:
    async def check_paid_auth(
        self: pyrogram.Client,
        phone_number: str,
        phone_code_hash: str,
        form_id: int,
    ) -> raw.base.auth.SentCode:
        """Check the status of a login payment.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            phone_number (``str``):
                Phone number.

            phone_code_hash (``str``):
                The phone code hash obtained from send_code.

            form_id (``int``):
                The payment form ID passed to payments.sendPaymentForm.

        Returns:
            :obj:`~pyrogram.raw.base.auth.SentCode`: Sent code status object.

        Example:
            .. code-block:: python

                sent_code = await app.check_paid_auth("+1234567890", code_hash, form_id)
        """
        return await self.invoke(
            raw.functions.auth.CheckPaidAuth(
                phone_number=phone_number,
                phone_code_hash=phone_code_hash,
                form_id=form_id,
            )
        )
