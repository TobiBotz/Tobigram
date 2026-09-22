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
from pyrogram import raw, types


class GetMessageAuthor:
    async def get_message_author(
        self: pyrogram.Client,
        chat_id: int | str,
        message_id: int,
    ) -> types.User:
        """Get the author of a message in a channel or supergroup.

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target channel or supergroup.

            message_id (``int``):
                The message ID to get the author for.

        Returns:
            :obj:`~pyrogram.types.User`: On success, the message author is returned.

        Example:
            .. code-block:: python

                author = await app.get_message_author(chat_id, 123)
        """
        peer = await self.resolve_peer(chat_id)

        r = await self.invoke(
            raw.functions.channels.GetMessageAuthor(
                channel=peer,
                id=message_id,
            )
        )

        return types.User._parse(self, r)
