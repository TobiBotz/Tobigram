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


class GetExtendedMedia:
    async def get_extended_media(
        self: pyrogram.Client,
        chat_id: int | str,
        message_ids: list[int],
    ) -> raw.base.Updates:
        """Request extended media for paid media messages.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            message_ids (List of ``int``):
                The IDs of the messages containing paid media.

        Returns:
            :obj:`~pyrogram.raw.base.Updates`: The updates object with extended media.

        Example:
            .. code-block:: python

                await app.get_extended_media(chat_id, [123, 456])
        """
        peer = await self.resolve_peer(chat_id)

        return await self.invoke(raw.functions.messages.GetExtendedMedia(peer=peer, id=message_ids))
