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

import logging
from typing import Union

import pyrogram
from pyrogram import raw, types, utils

log = logging.getLogger(__name__)


class SendEphemeralMessage:
    async def send_ephemeral_message(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        receiver_id: Union[int, str],
        text: str,
        query_id: int = None,
    ) -> "types.Message":
        """Send an ephemeral message visible only to a specific user and the bot in a group.

        .. include:: /_includes/usable-by/bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            receiver_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the user who will receive the ephemeral message.

            text (``str``):
                Text of the message to be sent.

            query_id (``int``, *optional*):
                Identifier of the guest query to respond to, if this message is a reply to a guest bot query.

        Returns:
            :obj:`~pyrogram.types.Message`: On success, the sent ephemeral message is returned.

        Example:
            .. code-block:: python

                # Send an ephemeral message to a specific user
                await app.send_ephemeral_message(chat_id, user_id, "Hello!")
        """
        r = await self.invoke(
            raw.functions.ephemeral.SendMessage(
                peer=await self.resolve_peer(chat_id),
                receiver_id=await self.resolve_peer(receiver_id),
                message=text,
                random_id=self.rnd_id(),
                query_id=query_id
            )
        )

        for u in getattr(r, "updates", []):
            if isinstance(u, raw.types.UpdateNewEphemeralMessage):
                return await types.Message._parse(
                    client=self,
                    message=u.message,
                    users={i.id: i for i in getattr(r, "users", [])},
                    chats={i.id: i for i in getattr(r, "chats", [])},
                )

        return None
