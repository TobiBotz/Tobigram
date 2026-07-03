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

# ***************************
# GENERATED FILE - DO NOT EDIT
# Source: tl:account.updateBusinessLocation
# ***************************

from typing import Union, Optional

import pyrogram
from pyrogram import raw
from pyrogram import types


class UpdateBusinessLocation:
    async def update_business_location(
        self: "pyrogram.Client",
        geo_point: raw.types.InputGeoPoint = None,
        address: str = None,
    ) -> "types.Message":
        """Update the business location shown on your business page.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            geo_point (raw.types.InputGeoPoint): Geolocation coordinates for the business
            address (str): Text address to display

        Returns:
            :obj:`~pyrogram.types.Message`

        Example:
            .. code-block:: python

                await app.update_business_location(...)
        """

        r = await self.invoke(
            raw.functions.account.updateBusinessLocation(
                geo_point=geo_point,
                address=address,
            )
        )
