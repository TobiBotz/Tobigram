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


class GetUnreadPollVotes:
    async def get_unread_poll_votes(
        self: pyrogram.Client,
        chat_id: int | str,
        offset_id: int = 0,
        add_offset: int = 0,
        limit: int = 100,
        max_id: int = 0,
        min_id: int = 0,
        top_msg_id: int | None = None,
    ) -> raw.base.messages.Messages:
        """Get unread poll votes in a chat.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            offset_id (``int``, *optional*):
                Only return messages starting from the specified id.

            add_offset (``int``, *optional*):
                Number of list elements to skip.

            limit (``int``, *optional*):
                Number of results to return. Defaults to 100.

            max_id (``int``, *optional*):
                If positive, only messages with IDs less than max_id will be returned.

            min_id (``int``, *optional*):
                If positive, only messages with IDs bigger than min_id will be returned.

            top_msg_id (``int``, *optional*):
                Thread/topic message ID.

        Returns:
            :obj:`~pyrogram.raw.base.messages.Messages`: The messages with unread poll votes.

        Example:
            .. code-block:: python

                msgs = await app.get_unread_poll_votes(chat_id)
        """
        peer = await self.resolve_peer(chat_id)

        return await self.invoke(
            raw.functions.messages.GetUnreadPollVotes(
                peer=peer,
                top_msg_id=top_msg_id,
                offset_id=offset_id,
                add_offset=add_offset,
                limit=limit,
                max_id=max_id,
                min_id=min_id,
            )
        )
