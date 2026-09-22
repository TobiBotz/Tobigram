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
from pyrogram import raw


class SendBotRequestedPeer:
    async def send_bot_requested_peer(
        self: pyrogram.Client,
        chat_id: int | str,
        message_id: int,
        button_id: int,
        requested_peers: list[raw.base.InputPeer],
        webapp_req_id: int | None = None,
    ) -> raw.base.Updates:
        """Send a peer chosen by the user via a ``KeyboardButtonRequestPeer`` button.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                The chat containing the button.

            message_id (``int``):
                The message ID with the button.

            button_id (``int``):
                The button ID.

            requested_peers (List of :obj:`~pyrogram.raw.base.InputPeer`):
                The peers chosen by the user.

            webapp_req_id (``int``, *optional*):
                Web app request ID.

        Returns:
            :obj:`~pyrogram.raw.base.Updates`: The updates object.

        Example:
            .. code-block:: python

                await app.send_bot_requested_peer(chat_id, message_id, button_id=1, requested_peers=[peer])
        """
        peer = await self.resolve_peer(chat_id)

        return await self.invoke(
            raw.functions.messages.SendBotRequestedPeer(
                peer=peer,
                msg_id=message_id,
                button_id=button_id,
                requested_peers=requested_peers,
                webapp_req_id=webapp_req_id,
            )
        )
