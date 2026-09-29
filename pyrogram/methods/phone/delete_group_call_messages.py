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
from pyrogram import raw, types, utils


class DeleteGroupCallMessages:
    async def delete_group_call_messages(
        self: pyrogram.Client,
        chat_id: int | str | raw.types.InputGroupCall | types.GroupCall,
        messages: list[int] | int,
        report_spam: bool | None = None,
    ) -> raw.base.Updates:
        """Delete messages sent in a group call or live stream chat.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            chat_id (``int`` | ``str`` | :obj:`~pyrogram.types.GroupCall`):
                Target chat ID or GroupCall object.

            messages (List of ``int`` | ``int``):
                List of message IDs or single message ID to delete.

            report_spam (``bool``, *optional*):
                Pass True to report the deleted messages as spam.

        Returns:
            :obj:`~pyrogram.raw.base.Updates`: Updates resulting from deleting messages.

        Example:
            .. code-block:: python

                await app.delete_group_call_messages(chat_id, messages=[123, 124])
        """
        if isinstance(chat_id, raw.types.InputGroupCall):
            call_input = chat_id
        elif hasattr(chat_id, "id") and hasattr(chat_id, "access_hash"):
            call_input = raw.types.InputGroupCall(id=chat_id.id, access_hash=chat_id.access_hash)
        else:
            peer = await self.resolve_peer(chat_id)
            full_chat = await self.invoke(
                raw.functions.channels.GetFullChannel(channel=utils.get_input_channel(peer))
                if isinstance(peer, (raw.types.InputPeerChannel, raw.types.InputChannel))
                else raw.functions.messages.GetFullChat(chat_id=peer.chat_id)
            )
            call_input = full_chat.full_chat.call

        if isinstance(messages, int):
            messages = [messages]

        return await self.invoke(
            raw.functions.phone.DeleteGroupCallMessages(
                call=call_input,
                messages=messages,
                report_spam=report_spam,
            )
        )
