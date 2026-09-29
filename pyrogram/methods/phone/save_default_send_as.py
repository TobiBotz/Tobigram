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


class SaveDefaultSendAs:
    async def save_default_send_as(
        self: pyrogram.Client,
        chat_id: int | str | raw.types.InputGroupCall | types.GroupCall,
        send_as: int | str | raw.base.InputPeer,
    ) -> bool:
        """Save the default peer identity displayed as author of live story comments/reactions.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str`` | :obj:`~pyrogram.types.GroupCall`):
                Target chat ID or live story GroupCall object.

            send_as (``int`` | ``str`` | :obj:`~pyrogram.raw.base.InputPeer`):
                Peer to display as author.

        Returns:
            ``bool``: On success, True is returned.

        Example:
            .. code-block:: python

                await app.save_default_send_as(chat_id, send_as="channel_username")
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

        if isinstance(send_as, raw.base.InputPeer):
            input_send_as = send_as
        else:
            input_send_as = await self.resolve_peer(send_as)

        return await self.invoke(
            raw.functions.phone.SaveDefaultSendAs(
                call=call_input,
                send_as=input_send_as,
            )
        )
