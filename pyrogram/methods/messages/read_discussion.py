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


class ReadDiscussion:
    async def read_discussion(
        self: pyrogram.Client,
        chat_id: int | str,
        message_id: int,
        read_max_id: int,
    ) -> bool:
        """Mark a discussion (comment thread) as read.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the channel.

            message_id (``int``):
                The message ID that started the discussion.

            read_max_id (``int``):
                The maximum message ID to mark as read in the discussion.

        Returns:
            ``bool``: True on success.

        Example:
            .. code-block:: python

                await app.read_discussion(chat_id, message_id, read_max_id=50)
        """
        peer = await self.resolve_peer(chat_id)

        return await self.invoke(
            raw.functions.messages.ReadDiscussion(
                peer=peer,
                msg_id=message_id,
                read_max_id=read_max_id,
            )
        )
