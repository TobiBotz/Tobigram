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
# Source: tl:bots.getBotInfo
# ***************************

from typing import Union, Optional

import pyrogram
from pyrogram import raw


class GetBotInfo:
    async def get_bot_info(
        self: "pyrogram.Client",
        bot: Optional[Union[int, str]] = None,
        lang_code: str = "en",
    ) -> "raw.types.bots.BotInfo":
        """Get bot info (name, about, description).

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            bot (Union[int, str], *optional*): Bot username or ID
            lang_code (str, *optional*): Language code for localized info

        Returns:
            :obj:`~pyrogram.raw.types.bots.BotInfo`

        Example:
            .. code-block:: python

                await app.get_bot_info(...)
        """

        r = await self.invoke(
            raw.functions.bots.GetBotInfo(
                bot=await self.resolve_peer(bot),
                lang_code=lang_code,
            )
        )

        return r
