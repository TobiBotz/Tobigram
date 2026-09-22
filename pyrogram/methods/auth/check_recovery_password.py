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


class CheckRecoveryPassword:
    async def check_recovery_password(
        self: pyrogram.Client,
        code: str,
    ) -> bool:
        """Check if the 2FA recovery code is valid before passing it to recover_password.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            code (``str``):
                Code received via email.

        Returns:
            ``bool``: On success, True is returned.

        Example:
            .. code-block:: python

                valid = await app.check_recovery_password("123456")
        """
        return await self.invoke(
            raw.functions.auth.CheckRecoveryPassword(
                code=code,
            )
        )
