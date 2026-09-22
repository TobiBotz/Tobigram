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


class DeleteAccount:
    async def delete_account(
        self: pyrogram.Client,
        reason: str = "",
        password: raw.base.InputCheckPasswordSRP | None = None,
    ) -> bool:
        """Delete the user's account from the telegram servers.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            reason (``str``, *optional*):
                Reason why the account is being deleted. Defaults to empty string.

            password (:obj:`~pyrogram.raw.base.InputCheckPasswordSRP`, *optional*):
                2FA password SRP parameters.

        Returns:
            ``bool``: On success, True is returned.
        """
        return await self.invoke(
            raw.functions.account.DeleteAccount(
                reason=reason,
                password=password,
            )
        )
