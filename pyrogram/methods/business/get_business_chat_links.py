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
# Source: tl:account.getBusinessChatLinks
# ***************************

from typing import Union, Optional

import pyrogram
from pyrogram import raw
from pyrogram import types


class GetBusinessChatLinks:
    async def get_business_chat_links(
        self: "pyrogram.Client",
    ) -> "types.BusinessChatLinks":
        """Get all business chat links.

        .. include:: /_includes/usable-by/users.rst

        Returns:
            :obj:`~pyrogram.types.BusinessChatLinks`

        Example:
            .. code-block:: python

                await app.get_business_chat_links(...)
        """

        r = await self.invoke(
            raw.functions.account.GetBusinessChatLinks(

            )
        )

        return types.BusinessChatLinks._parse(self, r)
