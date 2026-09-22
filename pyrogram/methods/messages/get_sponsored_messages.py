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


class GetSponsoredMessages:
    async def get_sponsored_messages(
        self: pyrogram.Client,
        chat_id: int | str,
        msg_id: int | None = None,
    ) -> raw.base.messages.SponsoredMessages:
        """Get sponsored messages for a channel.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target channel.

            msg_id (``int``, *optional*):
                Optional message ID context.

        Returns:
            :obj:`~pyrogram.raw.base.messages.SponsoredMessages`: The sponsored messages.

        Example:
            .. code-block:: python

                ads = await app.get_sponsored_messages(chat_id)
        """
        peer = await self.resolve_peer(chat_id)

        return await self.invoke(
            raw.functions.messages.GetSponsoredMessages(peer=peer, msg_id=msg_id)
        )
