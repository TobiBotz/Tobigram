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

# ***************************
# GENERATED FILE - DO NOT EDIT
# Source: tl:messages.getPollResults
# ***************************

from typing import Union, Optional

import pyrogram
from pyrogram import raw
from pyrogram import types


class GetPollResults:
    async def get_poll_results(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        msg_id: int,
    ) -> Optional["types.Poll"]:
        """Get the current results of a poll.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``): Chat where the poll message is
            msg_id (``int``): Message identifier (from the poll message)

        Returns:
            :obj:`~pyrogram.types.Poll`: On success, the poll with its updated results is returned.

        Example:
            .. code-block:: python

                await app.get_poll_results(chat_id, message_id)
        """

        r = await self.invoke(
            raw.functions.messages.GetPollResults(
                peer=await self.resolve_peer(chat_id),
                msg_id=msg_id,
                poll_hash=0,
            )
        )

        users = {i.id: i for i in r.users}
        chats = {i.id: i for i in r.chats}

        for i in r.updates:
            if isinstance(i, raw.types.UpdateMessagePoll):
                return await types.Poll._parse_update(self, i, users, chats)
