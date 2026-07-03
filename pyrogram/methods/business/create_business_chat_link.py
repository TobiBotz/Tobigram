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
# Source: tl:account.createBusinessChatLink
# ***************************

from typing import Union, Optional

import pyrogram
from pyrogram import raw
from pyrogram import types


class CreateBusinessChatLink:
    async def create_business_chat_link(
        self: "pyrogram.Client",
        link: raw.types.InputBusinessChatLink = None,
    ) -> "types.BusinessChatLink":
        """Create a business chat link with a predefined message.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            link (raw.types.InputBusinessChatLink): The chat link config (message, entities, title)

        Returns:
            :obj:`~pyrogram.types.BusinessChatLink`

        Example:
            .. code-block:: python

                await app.create_business_chat_link(...)
        """

        r = await self.invoke(
            raw.functions.account.createBusinessChatLink(
                link=link,
            )
        )
