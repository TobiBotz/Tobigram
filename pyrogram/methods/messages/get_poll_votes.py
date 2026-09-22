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


class GetPollVotes:
    async def get_poll_votes(
        self: pyrogram.Client,
        chat_id: int | str,
        message_id: int,
        option: bytes | None = None,
        offset: str | None = None,
        limit: int = 50,
    ) -> raw.base.messages.VotesList:
        """Get votes in a poll.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            message_id (``int``):
                The message ID of the poll.

            option (``bytes``, *optional*):
                The poll option data to filter votes by.

            offset (``str``, *optional*):
                Pagination offset.

            limit (``int``, *optional*):
                Maximum number of results. Defaults to 50.

        Returns:
            :obj:`~pyrogram.raw.base.messages.VotesList`: The list of votes.

        Example:
            .. code-block:: python

                votes = await app.get_poll_votes(chat_id, message_id)
        """
        peer = await self.resolve_peer(chat_id)

        return await self.invoke(
            raw.functions.messages.GetPollVotes(
                peer=peer,
                id=message_id,
                option=option,
                offset=offset,
                limit=limit,
            )
        )
