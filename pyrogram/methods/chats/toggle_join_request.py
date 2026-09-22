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


class ToggleJoinRequest:
    async def toggle_join_request(
        self: pyrogram.Client,
        chat_id: int | str,
        enabled: bool,
        apply_to_invites: bool | None = None,
        guard_bot: int | str | None = None,
    ) -> bool:
        """Toggle join requests (admin approval to join) on a channel or supergroup.

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target channel or supergroup.

            enabled (``bool``):
                Whether join requests should be enabled.

            apply_to_invites (``bool``, *optional*):
                Whether this applies to invite links.

            guard_bot (``int`` | ``str``, *optional*):
                Bot responsible for handling join requests.

        Returns:
            ``bool``: True on success.

        Example:
            .. code-block:: python

                # Enable join requests
                await app.toggle_join_request(chat_id, enabled=True)
        """
        peer = await self.resolve_peer(chat_id)
        bot_peer = await self.resolve_peer(guard_bot) if guard_bot else None

        await self.invoke(
            raw.functions.channels.ToggleJoinRequest(
                channel=peer,
                enabled=enabled,
                apply_to_invites=apply_to_invites,
                guard_bot=bot_peer,
            )
        )

        return True
