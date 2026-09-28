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


class ToggleSlowMode:
    async def toggle_slow_mode(
        self: pyrogram.Client,
        chat_id: int | str,
        seconds: int = 0,
    ) -> bool:
        """Toggle slow mode in a supergroup.

        .. include:: /_includes/usable-by/users.rst

        Parameters:

            seconds (int, *optional*): Slow mode interval in seconds (0 to disable)

            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.



        Returns:
            ``bool``: True on success.

        Example:
            .. code-block:: python

                await app.toggle_slow_mode(chat_id, ...)
        """

        await self.invoke(
            raw.functions.channels.ToggleSlowMode(
                channel=await self.resolve_peer(chat_id),
                seconds=seconds,
            )
        )

        return True
