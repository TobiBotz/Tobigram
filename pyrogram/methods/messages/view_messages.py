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

from typing import Iterable, Union

import pyrogram
from pyrogram import raw


class ViewMessages:
    async def view_messages(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        message_id: Union[int, Iterable[int]],
        increment: bool = True
    ) -> bool:
        """Increment the view counter of one or more messages.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            message_id (``int`` | Iterable of ``int``):
                Pass a single message identifier or an iterable of message ids to view.

            increment (``bool``, *optional*):
                Pass False to only read the view counters without incrementing them.
                Defaults to True.

        Returns:
            ``bool``: On success, True is returned.

        Example:
            .. code-block:: python

                await app.view_messages(chat_id, 12345)
        """

        ids = [message_id] if isinstance(message_id, int) else list(message_id)

        await self.invoke(
            raw.functions.messages.GetMessagesViews(
                peer=await self.resolve_peer(chat_id),
                id=ids,
                increment=increment
            )
        )

        return True
