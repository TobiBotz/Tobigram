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


class GetOutboxReadDate:
    async def get_outbox_read_date(
        self: pyrogram.Client,
        chat_id: int | str,
        message_id: int,
    ) -> raw.base.OutboxReadDate:
        """Get the date when the recipient read an outgoing message.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            message_id (``int``):
                The outgoing message ID to check.

        Returns:
            :obj:`~pyrogram.raw.base.OutboxReadDate`: The read date information.

        Example:
            .. code-block:: python

                info = await app.get_outbox_read_date(user_id, message_id)
        """
        peer = await self.resolve_peer(chat_id)

        return await self.invoke(
            raw.functions.messages.GetOutboxReadDate(peer=peer, msg_id=message_id)
        )
