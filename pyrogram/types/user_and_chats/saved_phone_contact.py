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

from datetime import datetime

import pyrogram
from pyrogram import raw, utils

from ..object import Object


class SavedPhoneContact(Object):
    """A saved phone contact.

    Parameters:
        phone (``str``):
            Phone number.

        first_name (``str``):
            First name.

        last_name (``str``):
            Last name.

        date (:py:obj:`~datetime.datetime`):
            Date the contact was saved.
    """

    def __init__(
        self,
        *,
        client: pyrogram.Client | None = None,
        phone: str,
        first_name: str,
        last_name: str,
        date: datetime,
    ):
        super().__init__(client)

        self.phone = phone
        self.first_name = first_name
        self.last_name = last_name
        self.date = date

    @staticmethod
    def _parse(
        client: pyrogram.Client,
        contact: raw.types.SavedPhoneContact,
    ) -> SavedPhoneContact | None:
        if not contact:
            return None

        return SavedPhoneContact(
            client=client,
            phone=contact.phone,
            first_name=contact.first_name,
            last_name=contact.last_name,
            date=utils.timestamp_to_datetime(contact.date),
        )
