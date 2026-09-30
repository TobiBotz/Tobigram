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


class EditGroupCallSettings:
    async def edit_group_call_settings(
        self: pyrogram.Client,
        chat_id: int | str | raw.types.InputGroupCall | types.GroupCall,
        join_muted: bool | None = None,
        messages_enabled: bool | None = None,
        reset_invite_hash: bool | None = None,
        send_paid_messages_stars: int | None = None,
    ) -> raw.base.Updates:
        """Edit settings for an active group voice chat (join muted, chat messages, stars).

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            chat_id (``int`` | ``str`` | :obj:`~pyrogram.types.GroupCall`):
                Unique identifier (int) or username (str) of the target chat, or the GroupCall object.

            join_muted (``bool``, *optional*):
                Whether new participants join muted by default.

            messages_enabled (``bool``, *optional*):
                Whether text messages are enabled during the call.

            reset_invite_hash (``bool``, *optional*):
                Whether to reset the invite link hash.

            send_paid_messages_stars (``int``, *optional*):
                Minimum stars required to send paid messages in the voice chat.

        Returns:
            :obj:`~pyrogram.raw.base.Updates`: On success, updates are returned.

        Example:
            .. code-block:: python

                # Mute new participants by default
                await app.edit_group_call_settings(chat_id, join_muted=True)
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

        return await self.invoke(
            raw.functions.phone.ToggleGroupCallSettings(
                call=call_input,
                join_muted=join_muted,
                messages_enabled=messages_enabled,
                reset_invite_hash=reset_invite_hash,
                send_paid_messages_stars=send_paid_messages_stars,
            )
        )
