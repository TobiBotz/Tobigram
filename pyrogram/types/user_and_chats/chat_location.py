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

from typing import Optional

import pyrogram
from pyrogram import raw, types

from ..object import Object


class ChatLocation(Object):
    """A location to which a supergroup is connected.

    Parameters:
        location (:obj:`~pyrogram.types.Location`):
            The location to which the supergroup is connected.

        address (``str``):
            Location address; 1-64 characters, as defined by the chat owner.
    """

    def __init__(
        self,
        *,
        client: Optional["pyrogram.Client"] = None,
        location: Optional["types.Location"] = None,
        address: Optional[str] = None
    ):
        super().__init__(client)

        self.location = location
        self.address = address

    @staticmethod
    def _parse(
        client,
        chat_location: "raw.base.ChannelLocation"
    ) -> Optional["ChatLocation"]:
        if not isinstance(chat_location, raw.types.ChannelLocation):
            return None

        return ChatLocation(
            client=client,
            location=types.Location._parse(chat_location.geo_point),
            address=chat_location.address
        )
