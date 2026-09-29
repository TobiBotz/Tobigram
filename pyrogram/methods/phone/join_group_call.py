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


class JoinGroupCall:
    async def join_group_call(
        self: pyrogram.Client,
        chat_id: int | str | raw.types.InputGroupCall | types.GroupCall,
        params: str | raw.base.DataJSON | None = None,
        join_as: int | str | raw.base.InputPeer | None = None,
        muted: bool | None = None,
        video_stopped: bool | None = None,
        invite_hash: str | None = None,
        public_key: int | None = None,
        block: bytes | None = None,
    ) -> raw.base.Updates:
        """Join a group call / voice chat via MTProto signaling.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            chat_id (``int`` | ``str`` | :obj:`~pyrogram.types.GroupCall`):
                Target chat ID or GroupCall object.

            params (``str`` | :obj:`~pyrogram.raw.base.DataJSON`, *optional*):
                Signaling parameters payload JSON string or DataJSON object.
                If omitted, a fresh random WebRTC SSRC is generated automatically.

            join_as (``int`` | ``str`` | :obj:`~pyrogram.raw.base.InputPeer`, *optional*):
                Channel or identity to join as. Defaults to self.

            muted (``bool``, *optional*):
                Whether to join muted.

            video_stopped (``bool``, *optional*):
                Whether to join with video disabled.

            invite_hash (``str``, *optional*):
                Invite hash to speak in a muted channel voice chat.

            public_key (``int``, *optional*):
                Conference call public key.

            block (``bytes``, *optional*):
                Conference call initial block.

        Returns:
            :obj:`~pyrogram.raw.base.Updates`: Updates resulting from joining the call.

        Example:
            .. code-block:: python

                await app.join_group_call(chat_id)
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

        if join_as is None:
            input_join_as = raw.types.InputPeerSelf()
        elif isinstance(join_as, raw.base.InputPeer):
            input_join_as = join_as
        else:
            input_join_as = await self.resolve_peer(join_as)

        current_params = params
        for attempt in range(3):
            if current_params is None:
                ssrc = random.randint(10000000, 99999999)
                param_obj = raw.types.DataJSON(
                    data=f'{{"ssrc": {ssrc}, "min_layer": 1, "max_layer": 92}}'
                )
            elif isinstance(current_params, str):
                param_obj = raw.types.DataJSON(data=current_params)
            else:
                param_obj = current_params

            try:
                return await self.invoke(
                    raw.functions.phone.JoinGroupCall(
                        call=call_input,
                        join_as=input_join_as,
                        params=param_obj,
                        muted=muted,
                        video_stopped=video_stopped,
                        invite_hash=invite_hash,
                        public_key=public_key,
                        block=block,
                    )
                )
            except Exception as e:
                if (
                    "GROUPCALL_SSRC_DUPLICATE_MUCH" in str(e)
                    or getattr(e, "ID", "") == "GROUPCALL_SSRC_DUPLICATE_MUCH"
                ) and attempt < 2:
                    current_params = None
                    continue
                raise
