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
# Source: tl:bots.canSendMessage
# ***************************

from typing import Union, Optional

import pyrogram
from pyrogram import raw
from pyrogram import types


class CanBotSendMessage:
    async def can_bot_send_message(
        self: "pyrogram.Client",
        bot: Optional[Union[int, str]] = None,
    ) -> "types.Message":
        """Check if a bot can send messages to the user.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            bot (Union[int, str], *optional*): Bot username or ID

        Returns:
            :obj:`~pyrogram.types.Message`

        Example:
            .. code-block:: python

                await app.can_bot_send_message(...)
        """

        r = await self.invoke(
            raw.functions.bots.CanSendMessage(
                bot=await self.resolve_peer(bot),
            )
        )
