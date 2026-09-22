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


class ToggleUserEmojiStatusPermission:
    async def toggle_user_emoji_status_permission(
        self: pyrogram.Client,
        bot: int | str,
        enabled: bool,
    ) -> bool:
        """Allow or prevent a bot from changing our emoji status.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            bot (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target bot.

            enabled (``bool``):
                Whether to allow (True) or prevent (False) the bot from changing our emoji status.

        Returns:
            ``bool``: On success, True is returned.

        Example:
            .. code-block:: python

                await app.toggle_user_emoji_status_permission("my_bot", True)
        """
        return await self.invoke(
            raw.functions.bots.ToggleUserEmojiStatusPermission(
                bot=await self.resolve_peer(bot),
                enabled=enabled,
            )
        )
