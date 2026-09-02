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
# Source: tl:messages.deleteScheduledMessages
# ***************************

from typing import Union, List, Optional

import pyrogram
from pyrogram import raw
from pyrogram import types


class DeleteScheduledMessages:
    async def delete_scheduled_messages(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        id: Optional[List[int]] = None,
    ) -> bool:
        """Delete scheduled messages.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:

            id (List[int], *optional*): List of message IDs to delete

            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.



        Returns:
            ``bool``: True on success.

        Example:
            .. code-block:: python

                await app.delete_scheduled_messages(chat_id, ...)
        """

        r = await self.invoke(
            raw.functions.messages.DeleteScheduledMessages(
                
                peer=await self.resolve_peer(chat_id),
                id=id,
            )
        )

        return any(isinstance(i, raw.types.UpdateDeleteScheduledMessages) for i in r.updates)
