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


class DeleteConferenceCallParticipants:
    async def delete_conference_call_participants(
        self: pyrogram.Client,
        chat_id: int | str | raw.types.InputGroupCall | types.GroupCall,
        ids: list[int] | int,
        only_left: bool | None = None,
        kick: bool | None = None,
        block: bytes | None = None,
    ) -> raw.base.Updates:
        """Remove or kick participants from an end-to-end encrypted conference call.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str`` | :obj:`~pyrogram.types.GroupCall`):
                Target chat ID or conference GroupCall object.

            ids (List of ``int`` | ``int``):
                Participant ID(s) to remove.

            only_left (``bool``, *optional*):
                Only delete participants who have already left.

            kick (``bool``, *optional*):
                Kick and ban participants from rejoining.

            block (``bytes``, *optional*):
                Conference call state update block.

        Returns:
            :obj:`~pyrogram.raw.base.Updates`: Updates resulting from removing participants.

        Example:
            .. code-block:: python

                await app.delete_conference_call_participants(chat_id, ids=[12345])
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

        if isinstance(ids, int):
            ids = [ids]

        return await self.invoke(
            raw.functions.phone.DeleteConferenceCallParticipants(
                call=call_input,
                ids=ids,
                only_left=only_left,
                kick=kick,
                block=block,
            )
        )
