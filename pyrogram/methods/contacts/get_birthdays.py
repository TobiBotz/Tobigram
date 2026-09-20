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
from pyrogram import raw, types


class GetBirthdays:
    async def get_birthdays(
        self: pyrogram.Client,
    ) -> types.List[types.ContactBirthday]:
        """Get contacts' upcoming birthdays.

        .. include:: /_includes/usable-by/users.rst

        Returns:
            List of :obj:`~pyrogram.types.ContactBirthday`: On success, a list of contact birthdays is returned.

        Example:
            .. code-block:: python

                birthdays = await app.get_birthdays()
                for item in birthdays:
                    print(item.contact_id, item.birthday.day, item.birthday.month)
        """
        r = await self.invoke(raw.functions.contacts.GetBirthdays())

        users = {u.id: u for u in getattr(r, "users", [])}

        return types.List(
            [types.ContactBirthday._parse(self, cb, users) for cb in getattr(r, "contacts", [])]
        )
