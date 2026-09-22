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


class VerifyPhone:
    async def verify_phone(
        self: pyrogram.Client,
        phone_number: str,
        phone_code_hash: str,
        phone_code: str,
    ) -> bool:
        """Verify a phone number for Telegram Passport.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            phone_number (``str``):
                Phone number.

            phone_code_hash (``str``):
                Phone code hash received from send_verify_phone_code.

            phone_code (``str``):
                SMS code received.

        Returns:
            ``bool``: On success, True is returned.
        """
        return await self.invoke(
            raw.functions.account.VerifyPhone(
                phone_number=phone_number,
                phone_code_hash=phone_code_hash,
                phone_code=phone_code,
            )
        )
