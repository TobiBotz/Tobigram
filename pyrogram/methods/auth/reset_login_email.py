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


class ResetLoginEmail:
    async def reset_login_email(
        self: pyrogram.Client,
        phone_number: str,
        phone_code_hash: str,
    ) -> raw.base.auth.SentCode:
        """Reset the login email.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            phone_number (``str``):
                Phone number of the account.

            phone_code_hash (``str``):
                Phone code hash obtained from send_code.

        Returns:
            :obj:`~pyrogram.raw.base.auth.SentCode`: Sent code status object.

        Example:
            .. code-block:: python

                sent_code = await app.reset_login_email("+1234567890", code_hash)
        """
        return await self.invoke(
            raw.functions.auth.ResetLoginEmail(
                phone_number=phone_number,
                phone_code_hash=phone_code_hash,
            )
        )
