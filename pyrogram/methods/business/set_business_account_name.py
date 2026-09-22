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


class SetBusinessAccountName:
    async def set_business_account_name(
        self: pyrogram.Client,
        business_connection_id: str,
        first_name: str,
        last_name: str | None = None,
    ) -> bool:
        """Change the first and last name of a managed business account.

        Requires the ``can_change_name`` business bot right.

        .. include:: /_includes/usable-by/bots.rst

        Parameters:
            business_connection_id (``str``):
                Unique identifier of the business connection.

            first_name (``str``):
                New first name for the business account; 1-64 characters.

            last_name (``str``, *optional*):
                New last name for the business account; 0-64 characters.
                Pass an empty string to remove the last name.

        Returns:
            ``bool``: True on success.

        Example:
            .. code-block:: python

                await app.set_business_account_name(connection_id, "Acme", "Corp")
        """
        await self.invoke(
            raw.functions.account.UpdateProfile(
                first_name=first_name,
                last_name=last_name if last_name is not None else "",
            ),
            business_connection_id=business_connection_id,
        )

        return True
