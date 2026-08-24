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


class DeleteWelcomeMessage:
    async def delete_welcome_message(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        message_id: int,
    ) -> bool:
        """Delete one of the welcome messages a bot has stored for a chat.

        .. include:: /_includes/usable-by/bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            message_id (``int``):
                Identifier of the welcome message to delete.

        Returns:
            ``bool``: True on success.

        Example:
            .. code-block:: python

                await app.delete_welcome_message(chat_id, message_id)
        """
        return await self.invoke(
            raw.functions.ephemeral.DeleteWelcomeMessage(
                peer=await self.resolve_peer(chat_id),
                id=message_id,
            )
        )
