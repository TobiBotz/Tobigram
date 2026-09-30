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


class EditGroupCallParticipant:
    async def edit_group_call_participant(
        self: pyrogram.Client,
        chat_id: int | str | raw.types.InputGroupCall | types.GroupCall,
        participant: int | str,
        muted: bool | None = None,
        volume: int | None = None,
        raise_hand: bool | None = None,
        video_stopped: bool | None = None,
        video_paused: bool | None = None,
        presentation_paused: bool | None = None,
    ) -> raw.base.Updates:
        """Edit participant properties in a group voice chat (mute, volume, video, hand raise).

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            chat_id (``int`` | ``str`` | :obj:`~pyrogram.types.GroupCall`):
                Unique identifier (int) or username (str) of the target chat, or the GroupCall object.

            participant (``int`` | ``str``):
                Target user identifier to edit.

            muted (``bool``, *optional*):
                Pass True to mute the participant, False to unmute.

            volume (``int``, *optional*):
                Set participant's volume level (1 to 20000, 10000 = 100%).

            raise_hand (``bool``, *optional*):
                Pass True to raise hand in voice chat, False to lower hand.

            video_stopped (``bool``, *optional*):
                Pass True if participant's video is stopped.

            video_paused (``bool``, *optional*):
                Pass True if participant's video is paused.

            presentation_paused (``bool``, *optional*):
                Pass True if participant's screen share presentation is paused.

        Returns:
            :obj:`~pyrogram.raw.base.Updates`: On success, updates are returned.

        Example:
            .. code-block:: python

                # Mute a participant
                await app.edit_group_call_participant(chat_id, user_id, muted=True)

                # Unmute a participant
                await app.edit_group_call_participant(chat_id, user_id, muted=False)
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

        participant_peer = await self.resolve_peer(participant)

        return await self.invoke(
            raw.functions.phone.EditGroupCallParticipant(
                call=call_input,
                participant=participant_peer,
                muted=muted,
                volume=volume,
                raise_hand=raise_hand,
                video_stopped=video_stopped,
                video_paused=video_paused,
                presentation_paused=presentation_paused,
            )
        )
