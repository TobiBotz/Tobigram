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


class GetSavedContacts:
    async def get_saved_contacts(
        self: pyrogram.Client,
    ) -> types.List[types.SavedPhoneContact]:
        """Get list of saved phone contacts.

        .. include:: /_includes/usable-by/users.rst

        Returns:
            List of :obj:`~pyrogram.types.SavedPhoneContact`: On success, a list of saved phone contacts is returned.

        Example:
            .. code-block:: python

                saved = await app.get_saved_contacts()
                for contact in saved:
                    print(contact.phone, contact.first_name, contact.last_name)
        """
        r = await self.invoke(raw.functions.contacts.GetSaved())

        return types.List([types.SavedPhoneContact._parse(self, c) for c in r])
