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


class ToggleConnectedBotPaused:
    async def toggle_connected_bot_paused(
        self: pyrogram.Client,
        peer: int | str | raw.base.InputPeer,
        paused: bool,
    ) -> bool:
        """Pause or unpause a specific chat, temporarily disconnecting it from all business bots.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            peer (``int`` | ``str`` | :obj:`~pyrogram.raw.base.InputPeer`):
                The chat to pause or unpause.

            paused (``bool``):
                Whether to pause or unpause the chat.

        Returns:
            ``bool``: On success, True is returned.
        """
        input_peer = peer if isinstance(peer, raw.base.InputPeer) else await self.resolve_peer(peer)

        return await self.invoke(
            raw.functions.account.ToggleConnectedBotPaused(
                peer=input_peer,
                paused=paused,
            )
        )
