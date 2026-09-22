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


class GetMessagePublicForwards:
    async def get_message_public_forwards(
        self: pyrogram.Client,
        chat_id: int | str,
        message_id: int,
        offset: str = "",
        limit: int = 10,
    ) -> raw.base.stats.PublicForwards:
        """Obtain a list of public channel forwards for a message.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target channel.

            message_id (``int``):
                Message ID.

            offset (``str``, *optional*):
                Offset for pagination. Defaults to empty string.

            limit (``int``, *optional*):
                Maximum number of results to return. Defaults to 10.

        Returns:
            :obj:`~pyrogram.raw.base.stats.PublicForwards`: The public forwards.

        Example:
            .. code-block:: python

                forwards = await app.get_message_public_forwards(chat_id, message_id)
        """
        return await self.invoke(
            raw.functions.stats.GetMessagePublicForwards(
                channel=await self.resolve_peer(chat_id),
                msg_id=message_id,
                offset=offset,
                limit=limit,
            )
        )
