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


class EditChatLocation:
    async def edit_chat_location(
        self: pyrogram.Client,
        chat_id: int | str,
        latitude: float,
        longitude: float,
        address: str,
    ) -> bool:
        """Edit the location of a geogroup.

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target supergroup.

            latitude (``float``):
                Latitude of the new location.

            longitude (``float``):
                Longitude of the new location.

            address (``str``):
                Address of the new location.

        Returns:
            ``bool``: True on success.

        Example:
            .. code-block:: python

                await app.edit_chat_location(chat_id, 37.7749, -122.4194, "San Francisco, CA")
        """
        peer = await self.resolve_peer(chat_id)

        return await self.invoke(
            raw.functions.channels.EditLocation(
                channel=peer,
                geo_point=raw.types.InputGeoPoint(lat=latitude, long=longitude),
                address=address,
            )
        )
