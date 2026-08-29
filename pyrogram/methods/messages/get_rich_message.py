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

from typing import Union

import pyrogram
from pyrogram import raw
from pyrogram import types
from pyrogram import utils


class GetRichMessage:
    async def get_rich_message(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        message_id: int,
    ) -> "types.Message":
        """Get the full rich message of a message that arrived truncated.

        A rich message larger than the inline byte limit is delivered with only its first
        blocks and ``is_partial`` set on its :obj:`~pyrogram.types.RichMessage`; this fetches
        the whole of it.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".

            message_id (``int``):
                Unique identifier of the message whose rich message is to be fetched.

        Returns:
            :obj:`~pyrogram.types.Message`: On success, the message with its complete
            ``rich_message`` is returned.

        Example:
            .. code-block:: python

                if message.rich_message.is_partial:
                    message = await app.get_rich_message(message.chat.id, message.id)
        """
        r = await self.invoke(
            raw.functions.messages.GetRichMessage(
                peer=await self.resolve_peer(chat_id),
                id=message_id,
            )
        )

        messages = await utils.parse_messages(self, r, replies=0)

        return messages[0] if messages else None
