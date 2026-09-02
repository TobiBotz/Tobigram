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

from typing import List, Union

import pyrogram
from pyrogram import raw, types


class GetWelcomeMessages:
    async def get_welcome_messages(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
    ) -> List["types.Message"]:
        """Get the welcome messages a bot has stored for a chat.

        A welcome message is an ephemeral message sent with ``welcome=True``, kept by the
        server as a template and shown to each user the first time they open the chat,
        rather than delivered once.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

        Returns:
            List of :obj:`~pyrogram.types.Message`: The stored welcome messages.

        Example:
            .. code-block:: python

                for message in await app.get_welcome_messages(chat_id):
                    print(message.text)
        """
        r = await self.invoke(
            raw.functions.ephemeral.GetWelcomeMessages(
                peer=await self.resolve_peer(chat_id),
                hash=0,
            )
        )

        if isinstance(r, raw.types.ephemeral.WelcomeMessagesNotModified):
            return types.List()

        users = {i.id: i for i in getattr(r, "users", [])}
        chats = {i.id: i for i in getattr(r, "chats", [])}

        return types.List(
            [
                await types.Message._parse(self, message, users, chats)
                for message in r.messages
            ]
        )
