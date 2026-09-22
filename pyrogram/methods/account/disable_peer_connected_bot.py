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


class DisablePeerConnectedBot:
    async def disable_peer_connected_bot(
        self: pyrogram.Client,
        peer: int | str | raw.base.InputPeer,
    ) -> bool:
        """Permanently disconnect a specific chat from all business bots.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            peer (``int`` | ``str`` | :obj:`~pyrogram.raw.base.InputPeer`):
                The chat to disconnect.

        Returns:
            ``bool``: On success, True is returned.
        """
        input_peer = peer if isinstance(peer, raw.base.InputPeer) else await self.resolve_peer(peer)

        return await self.invoke(
            raw.functions.account.DisablePeerConnectedBot(
                peer=input_peer,
            )
        )
