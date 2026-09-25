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
from pyrogram import raw, types, utils

from ..object import Object
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime


class ReadParticipantDate(Object):
    """Contains information about when a participant read a specific message.

    Parameters:
        user_id (``int``):
            The ID of the user who read the message.

        date (:py:obj:`~datetime.datetime`):
            Date and time when the user read the message.

        user (:obj:`~pyrogram.types.User`, *optional*):
            The user object, if available.
    """

    def __init__(
        self,
        *,
        client: pyrogram.Client | None = None,
        user_id: int,
        date: datetime,
        user: types.User | None = None,
    ):
        super().__init__(client)

        self.user_id = user_id
        self.date = date
        self.user = user

    @staticmethod
    def _parse(
        client: pyrogram.Client,
        read_date: raw.types.ReadParticipantDate,
        users: dict[int, raw.types.User] | None = None,
    ) -> ReadParticipantDate:
        user = None
        if users and read_date.user_id in users:
            user = types.User._parse(client, users[read_date.user_id])

        return ReadParticipantDate(
            client=client,
            user_id=read_date.user_id,
            date=utils.timestamp_to_datetime(read_date.date),
            user=user,
        )
