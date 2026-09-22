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


class ToggleBotUsername:
    async def toggle_bot_username(
        self: pyrogram.Client,
        bot: int | str,
        username: str,
        active: bool,
    ) -> bool:
        """Activate or deactivate a purchased fragment.com username associated to a bot we own.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            bot (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target bot.

            username (``str``):
                The username to toggle.

            active (``bool``):
                Whether to activate (True) or deactivate (False) the username.

        Returns:
            ``bool``: On success, True is returned.

        Example:
            .. code-block:: python

                await app.toggle_bot_username("my_bot", "cool_bot", True)
        """
        return await self.invoke(
            raw.functions.bots.ToggleUsername(
                bot=await self.resolve_peer(bot),
                username=username,
                active=active,
            )
        )
