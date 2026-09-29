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


class GetGroupCall:
    async def get_group_call(
        self: pyrogram.Client,
        chat_id: int | str,
    ) -> types.GroupCall | None:
        """Get details about an active group voice chat or live stream.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

        Returns:
            :obj:`~pyrogram.types.GroupCall` | None: On success, group call details are returned.

        Example:
            .. code-block:: python

                call = await app.get_group_call(chat_id)
                print(call.participants_count)
        """
        peer = await self.resolve_peer(chat_id)

        full_chat = await self.invoke(
            raw.functions.channels.GetFullChannel(channel=utils.get_input_channel(peer))
            if isinstance(peer, (raw.types.InputPeerChannel, raw.types.InputChannel))
            else raw.functions.messages.GetFullChat(chat_id=peer.chat_id)
        )

        call_info = full_chat.full_chat.call
        if not call_info:
            return None

        raw_group_call = await self.invoke(
            raw.functions.phone.GetGroupCall(
                call=call_info,
                limit=1,
            )
        )

        return types.GroupCall._parse(self, raw_group_call.call)
