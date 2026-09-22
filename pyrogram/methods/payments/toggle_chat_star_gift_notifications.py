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


class ToggleChatStarGiftNotifications:
    async def toggle_chat_star_gift_notifications(
        self: pyrogram.Client,
        chat_id: int | str,
        enabled: bool = True,
    ) -> bool:
        """Toggle notifications for incoming star gifts in a channel or chat.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Target chat ID.

            enabled (``bool``, *optional*):
                Whether notifications should be enabled. Defaults to True.

        Returns:
            ``bool``: True on success.

        Example:
            .. code-block:: python

                await app.toggle_chat_star_gift_notifications(chat_id, True)
        """
        peer = await self.resolve_peer(chat_id)

        return await self.invoke(
            raw.functions.payments.ToggleChatStarGiftNotifications(
                peer=peer,
                enabled=enabled,
            )
        )
