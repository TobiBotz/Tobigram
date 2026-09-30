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


class LeaveGroupCall:
    async def leave_group_call(
        self: pyrogram.Client,
        chat_id: int | str | raw.types.InputGroupCall | types.GroupCall,
        source: int | None = None,
    ) -> bool | raw.base.Updates:
        """Leave an active group voice chat or video stream without ending the call for others.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str`` | :obj:`~pyrogram.types.GroupCall`):
                Unique identifier (int) or username (str) of the target chat, or GroupCall object.

            source (``int``, *optional*):
                Source ID of the main group call stream if leaving via raw signaling.
                If not specified, leaves using the active WebRTC call manager.

        Returns:
            ``bool`` | :obj:`~pyrogram.raw.base.Updates`: True on success, or Updates if raw call left.

        Example:
            .. code-block:: python

                await app.leave_group_call(chat_id)
        """
        try:
            await self.calls.leave(chat_id=chat_id)
        except Exception:
            pass

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

        if not call_input:
            return True

        return await self.invoke(
            raw.functions.phone.LeaveGroupCall(
                call=call_input,
                source=source or 0,
            )
        )
