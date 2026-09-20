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


class DeleteFactCheck:
    async def delete_fact_check(
        self: pyrogram.Client,
        chat_id: int | str | None = None,
        message_id: int | None = None,
        peer: int | str | None = None,
        msg_id: int | None = None,
    ) -> types.Message:
        """Delete the fact-check on a message (channel admins only).

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``, *optional*):
                Unique identifier (int) or username (str) of the target chat.

            message_id (``int``, *optional*):
                Message ID from which to delete the fact-check.

            peer (``int`` | ``str``, *optional*):
                Alias for *chat_id*.

            msg_id (``int``, *optional*):
                Alias for *message_id*.

        Returns:
            :obj:`~pyrogram.types.Message`: On success, the updated message is returned.

        Example:
            .. code-block:: python

                await app.delete_fact_check(chat_id, message_id)
        """
        chat_id = chat_id if chat_id is not None else peer
        message_id = message_id if message_id is not None else msg_id

        if chat_id is None or message_id is None:
            raise ValueError("chat_id and message_id are required")

        r = await self.invoke(
            raw.functions.messages.DeleteFactCheck(
                peer=await self.resolve_peer(chat_id),
                msg_id=message_id,
            )
        )

        for i in r.updates:
            if isinstance(
                i,
                (
                    raw.types.UpdateEditMessage,
                    raw.types.UpdateEditChannelMessage,
                    raw.types.UpdateEditEphemeralMessage,
                ),
            ):
                return await types.Message._parse(
                    self, i.message, {u.id: u for u in r.users}, {c.id: c for c in r.chats}
                )
