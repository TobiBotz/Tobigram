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

import random

import pyrogram
from pyrogram import raw, types, utils


class SendGroupCallMessage:
    async def send_group_call_message(
        self: pyrogram.Client,
        chat_id: int | str | raw.types.InputGroupCall | types.GroupCall,
        message: str,
        allow_paid_stars: int | None = None,
        send_as: int | str | None = None,
    ) -> raw.base.Updates:
        """Send a live chat text message during an active group voice chat or live stream.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str`` | :obj:`~pyrogram.types.GroupCall`):
                Unique identifier (int) or username (str) of the target chat, or the GroupCall object.

            message (``str``):
                Text of the message to send.

            allow_paid_stars (``int``, *optional*):
                Stars to tip along with the message, if paid messages are enabled.

            send_as (``int`` | ``str``, *optional*):
                Peer to send the message as (personal profile or channel).

        Returns:
            :obj:`~pyrogram.raw.base.Updates`: On success, updates are returned.
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

        text, entities = (await self.parser.parse(message)).values()
        send_as_peer = await self.resolve_peer(send_as) if send_as else None

        return await self.invoke(
            raw.functions.phone.SendGroupCallMessage(
                call=call_input,
                random_id=random.randint(1, 9223372036854775807),
                message=raw.types.TextWithEntities(text=text, entities=entities or []),
                allow_paid_stars=allow_paid_stars,
                send_as=send_as_peer,
            )
        )
