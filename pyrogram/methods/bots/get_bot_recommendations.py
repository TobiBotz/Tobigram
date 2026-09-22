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


class GetBotRecommendations:
    async def get_bot_recommendations(
        self: pyrogram.Client,
        bot: int | str,
    ) -> raw.base.users.Users:
        """Obtain a list of similarly themed bots based on similarities in subscriber bases.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            bot (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target bot.

        Returns:
            :obj:`~pyrogram.raw.base.users.Users`: List of recommended bots.

        Example:
            .. code-block:: python

                bots = await app.get_bot_recommendations("my_bot")
        """
        return await self.invoke(
            raw.functions.bots.GetBotRecommendations(
                bot=await self.resolve_peer(bot),
            )
        )
