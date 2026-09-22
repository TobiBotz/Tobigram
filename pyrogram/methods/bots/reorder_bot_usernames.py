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


class ReorderBotUsernames:
    async def reorder_bot_usernames(
        self: pyrogram.Client,
        bot: int | str,
        order: list[str],
    ) -> bool:
        """Reorder active usernames associated to a bot we own.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            bot (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target bot.

            order (List of ``str``):
                The new order for active usernames. All active usernames must be specified.

        Returns:
            ``bool``: On success, True is returned.

        Example:
            .. code-block:: python

                await app.reorder_bot_usernames("my_bot", ["user1_bot", "user2_bot"])
        """
        return await self.invoke(
            raw.functions.bots.ReorderUsernames(
                bot=await self.resolve_peer(bot),
                order=order,
            )
        )
