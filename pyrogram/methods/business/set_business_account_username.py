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


class SetBusinessAccountUsername:
    async def set_business_account_username(
        self: pyrogram.Client,
        business_connection_id: str,
        username: str | None = None,
    ) -> bool:
        """Change the username of a managed business account.

        Requires the ``can_change_username`` business bot right.

        .. include:: /_includes/usable-by/bots.rst

        Parameters:
            business_connection_id (``str``):
                Unique identifier of the business connection.

            username (``str``, *optional*):
                New username for the business account; 0-32 characters.
                Pass an empty string or omit to remove the username.

        Returns:
            ``bool``: True on success.

        Example:
            .. code-block:: python

                await app.set_business_account_username(connection_id, "myshop")
        """
        await self.invoke(
            raw.functions.account.UpdateUsername(
                username=username if username is not None else "",
            ),
            business_connection_id=business_connection_id,
        )

        return True
