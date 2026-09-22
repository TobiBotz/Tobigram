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


class ToggleNoPaidMessagesException:
    async def toggle_no_paid_messages_exception(
        self: pyrogram.Client,
        user_id: int | str | raw.base.InputUser,
        refund_charged: bool | None = None,
        require_payment: bool | None = None,
        parent_peer: int | str | raw.base.InputPeer | None = None,
    ) -> bool:
        """Allow a user to send messages without paying if paid messages are enabled.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            user_id (``int`` | ``str`` | :obj:`~pyrogram.raw.base.InputUser`):
                The user to exempt or unexempt.

            refund_charged (``bool``, *optional*):
                Whether to refund the amounts already paid.

            require_payment (``bool``, *optional*):
                Whether to require payment.

            parent_peer (``int`` | ``str`` | :obj:`~pyrogram.raw.base.InputPeer`, *optional*):
                Channel or monoforum peer.

        Returns:
            ``bool``: On success, True is returned.
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
            raw.functions.account.ToggleNoPaidMessagesException(
                user_id=input_user,
                refund_charged=refund_charged,
                require_payment=require_payment,
                parent_peer=input_parent,
            )
        )
