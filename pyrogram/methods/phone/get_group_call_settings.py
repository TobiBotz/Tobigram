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


class GetGroupCallSettings:
    async def get_group_call_settings(
        self: pyrogram.Client,
        chat_id: int | str | raw.types.InputGroupCall | types.GroupCall,
    ) -> types.GroupCallSettings | None:
        """Get current settings of an active group voice chat or live stream.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str`` | :obj:`~pyrogram.types.GroupCall`):
                Unique identifier (int) or username (str) of the target chat, or the GroupCall object.

        Returns:
            :obj:`~pyrogram.types.GroupCallSettings` | None: On success, group call settings are returned.

        Example:
            .. code-block:: python

                settings = await app.get_group_call_settings(chat_id)
                print(settings.join_muted)
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

        if not call_input:
            return None

        raw_group_call = await self.invoke(
            raw.functions.phone.GetGroupCall(
                call=call_input,
                limit=1,
            )
        )
        c = raw_group_call.call
        if not isinstance(c, raw.types.GroupCall):
            return None

        return types.GroupCallSettings(
            client=self,
            join_muted=bool(getattr(c, "join_muted", False)),
            messages_enabled=bool(getattr(c, "messages_enabled", True)),
            listeners_hidden=getattr(c, "listeners_hidden", None),
            send_paid_messages_stars=getattr(c, "send_paid_messages_stars", None),
            can_change_join_muted=getattr(c, "can_change_join_muted", None),
            can_change_messages_enabled=getattr(c, "can_change_messages_enabled", None),
        )
