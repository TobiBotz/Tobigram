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

from typing import List

import pyrogram
from pyrogram import raw


class GetBusinessChatLinks:
    async def get_business_chat_links(
        self: "pyrogram.Client",
    ) -> List["raw.types.BusinessChatLink"]:
        """Get all business chat links.

        .. include:: /_includes/usable-by/users.rst

        Returns:
            List of :obj:`~pyrogram.raw.types.BusinessChatLink`

        Example:
            .. code-block:: python

                await app.get_business_chat_links(...)
        """

        r = await self.invoke(
            raw.functions.account.GetBusinessChatLinks(

            )
        )

        return r.links
