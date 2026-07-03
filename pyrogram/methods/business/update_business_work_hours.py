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
# Source: tl:account.updateBusinessWorkHours
# ***************************

from typing import Union, Optional

import pyrogram
from pyrogram import raw
from pyrogram import types


class UpdateBusinessWorkHours:
    async def update_business_work_hours(
        self: "pyrogram.Client",
        business_work_hours: raw.types.BusinessWorkHours = None,
    ) -> "types.Message":
        """Update business work hours for your business account.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            business_work_hours (raw.types.BusinessWorkHours): Business work hours (timezone + weekly schedule)

        Returns:
            :obj:`~pyrogram.types.Message`

        Example:
            .. code-block:: python

                await app.update_business_work_hours(...)
        """

        r = await self.invoke(
            raw.functions.account.updateBusinessWorkHours(
                business_work_hours=business_work_hours,
            )
        )
