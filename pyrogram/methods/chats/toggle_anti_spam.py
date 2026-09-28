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


class ToggleAntiSpam:
    async def toggle_anti_spam(
        self: pyrogram.Client,
        chat_id: int | str,
        enabled: bool | None = None,
    ) -> bool:
        """Toggle the anti-spam filter in a supergroup.

        .. include:: /_includes/usable-by/users.rst

        Parameters:

            enabled (bool, *optional*): Whether anti-spam is enabled

            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.



        Returns:
            ``bool``: True on success.

        Example:
            .. code-block:: python

                await app.toggle_anti_spam(chat_id, ...)
        """

        await self.invoke(
            raw.functions.channels.ToggleAntiSpam(
                channel=await self.resolve_peer(chat_id),
                enabled=enabled,
            )
        )

        return True
