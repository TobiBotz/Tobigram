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


class ReportMissingCode:
    async def report_missing_code(
        self: pyrogram.Client,
        phone_number: str,
        phone_code_hash: str,
        mnc: str,
    ) -> bool:
        """Report that the SMS authentication code was not delivered.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            phone_number (``str``):
                Phone number where the code was supposed to be delivered.

            phone_code_hash (``str``):
                The phone code hash obtained from send_code.

            mnc (``str``):
                Mobile Network Code (MNC) of the current network operator.

        Returns:
            ``bool``: On success, True is returned.

        Example:
            .. code-block:: python

                await app.report_missing_code("+1234567890", code_hash, "01")
        """
        return await self.invoke(
            raw.functions.auth.ReportMissingCode(
                phone_number=phone_number,
                phone_code_hash=phone_code_hash,
                mnc=mnc,
            )
        )
