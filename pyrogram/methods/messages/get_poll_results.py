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
        chat_id: Optional[Union[int, str]] = None,
        msg_id: Optional[int] = None,
    ) -> "types.Message":
        """Get poll results for a message.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (Union[int, str], *optional*): Chat where the poll message is
            msg_id (int, *optional*): Message identifier (from the poll message)

        Returns:
            :obj:`~pyrogram.types.Message`

        Example:
            .. code-block:: python

                await app.get_poll_results(...)
        """

        r = await self.invoke(
            raw.functions.messages.getPollResults(
                peer=await self.resolve_peer(peer),
                msg_id=msg_id,
            )
        )

        for i in r.updates:
            if isinstance(i, (raw.types.UpdateNewMessage,
                              raw.types.UpdateNewChannelMessage,
                              raw.types.UpdateNewScheduledMessage)):
                return await types.Message._parse(
                    self, i.message,
                    {i.id: i for i in r.users},
                    {i.id: i for i in r.chats},
                    is_scheduled=isinstance(i, raw.types.UpdateNewScheduledMessage)
                )
