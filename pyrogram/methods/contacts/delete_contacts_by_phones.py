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


class DeleteContactsByPhones:
    async def delete_contacts_by_phones(
        self: pyrogram.Client,
        phones: list[str],
    ) -> bool:
        """Delete contacts by phone number.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            phones (List of ``str``):
                Phone numbers to delete from contacts.

        Returns:
            ``bool``: On success, True is returned.

        Example:
            .. code-block:: python

                await app.delete_contacts_by_phones(["+1234567890", "+9876543210"])
        """
        return await self.invoke(
            raw.functions.contacts.DeleteByPhones(
                phones=phones,
            )
        )
