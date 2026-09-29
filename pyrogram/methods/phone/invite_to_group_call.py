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


class InviteToGroupCall:
    async def invite_to_group_call(
        self: pyrogram.Client,
        chat_id: int | str | raw.types.InputGroupCall | types.GroupCall,
        users: list[int | str] | int | str,
    ) -> raw.base.Updates:
        """Invite one or more users to an active group voice chat.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            chat_id (``int`` | ``str`` | :obj:`~pyrogram.types.GroupCall`):
                Unique identifier (int) or username (str) of the target chat, or the GroupCall object.

            users (List of ``int`` | ``str`` | ``int`` | ``str``):
                List of user identifiers, or a single user identifier.

        Returns:
            :obj:`~pyrogram.raw.base.Updates`: On success, updates are returned.

        Example:
            .. code-block:: python

                await app.invite_to_group_call(chat_id, [1234567, "username"])
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
            if not full_chat.full_chat.call:
                raise ValueError(f"No voice chat found in {chat_id}")
            call_input = full_chat.full_chat.call

        if not isinstance(users, list):
            users = [users]

        input_users = [await self.resolve_peer(u) for u in users]
        input_user_objects = [
            raw.types.InputUser(user_id=p.user_id, access_hash=p.access_hash)
            if isinstance(p, raw.types.InputPeerUser)
            else await self.resolve_peer(p)
            for p in input_users
        ]

        return await self.invoke(
            raw.functions.phone.InviteToGroupCall(
                call=call_input,
                users=input_user_objects,
            )
        )
