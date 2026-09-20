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

from ..object import Object


class ContactBirthday(Object):
    """Birthday information of a contact.

    Parameters:
        contact_id (``int``):
            Unique identifier of the contact user.

        birthday (:obj:`~pyrogram.types.Birthday`):
            Birthday details.

        user (:obj:`~pyrogram.types.User`, *optional*):
            User object representing this contact, if available.
    """

    def __init__(
        self,
        *,
        client: pyrogram.Client | None = None,
        contact_id: int,
        birthday: types.Birthday,
        user: types.User | None = None,
    ):
        super().__init__(client)

        self.contact_id = contact_id
        self.birthday = birthday
        self.user = user

    @staticmethod
    def _parse(
        client: pyrogram.Client,
        contact_birthday: raw.types.ContactBirthday,
        users: dict[int, raw.types.User] | None = None,
    ) -> ContactBirthday | None:
        if not contact_birthday:
            return None

        users = users or {}
        raw_user = users.get(contact_birthday.contact_id)
        user = types.User._parse(client, raw_user) if raw_user else None

        return ContactBirthday(
            client=client,
            contact_id=contact_birthday.contact_id,
            birthday=types.Birthday._parse(contact_birthday.birthday),
            user=user,
        )
