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


class GetPaidMessagesRevenue:
    async def get_paid_messages_revenue(
        self: pyrogram.Client,
        user_id: int | str | raw.base.InputUser,
        parent_peer: int | str | raw.base.InputPeer | None = None,
    ) -> raw.base.account.PaidMessagesRevenue:
        """Get the number of stars received from the specified user via paid messages.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            user_id (``int`` | ``str`` | :obj:`~pyrogram.raw.base.InputUser`):
                The user that paid to send messages.

            parent_peer (``int`` | ``str`` | :obj:`~pyrogram.raw.base.InputPeer`, *optional*):
                Channel or monoforum peer.

        Returns:
            :obj:`~pyrogram.raw.base.account.PaidMessagesRevenue`: On success, revenue details are returned.
        """
        input_user = (
            user_id if isinstance(user_id, raw.base.InputUser) else await self.resolve_peer(user_id)
        )
        input_parent = None
        if parent_peer is not None:
            input_parent = (
                parent_peer
                if isinstance(parent_peer, raw.base.InputPeer)
                else await self.resolve_peer(parent_peer)
            )

        return await self.invoke(
            raw.functions.account.GetPaidMessagesRevenue(
                user_id=input_user,
                parent_peer=input_parent,
            )
        )
