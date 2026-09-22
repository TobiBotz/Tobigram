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


class GetSecureValue:
    async def get_secure_value(
        self: pyrogram.Client,
        types: list[raw.base.SecureValueType],
    ) -> list[raw.base.SecureValue]:
        """Get saved Telegram Passport documents.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            types (List of :obj:`~pyrogram.raw.base.SecureValueType`):
                Requested value types.

        Returns:
            List of :obj:`~pyrogram.raw.base.SecureValue`: On success, secure values are returned.
        """
        return await self.invoke(
            raw.functions.account.GetSecureValue(
                types=types,
            )
        )
