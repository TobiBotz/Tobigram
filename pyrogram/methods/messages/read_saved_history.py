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


class ReadSavedHistory:
    async def read_saved_history(
        self: pyrogram.Client,
        parent_peer: int | str,
        peer: int | str,
        max_id: int = 0,
    ) -> bool:
        """Mark saved messages history as read up to a given message ID.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            parent_peer (``int`` | ``str``):
                The parent peer (usually "me").

            peer (``int`` | ``str``):
                The peer whose saved messages to mark as read.

            max_id (``int``, *optional*):
                The maximum message ID to mark as read.

        Returns:
            ``bool``: True on success.

        Example:
            .. code-block:: python

                await app.read_saved_history("me", user_id, max_id=100)
        """
        parent = await self.resolve_peer(parent_peer)
        saved_peer = await self.resolve_peer(peer)

        return await self.invoke(
            raw.functions.messages.ReadSavedHistory(
                parent_peer=parent,
                peer=saved_peer,
                max_id=max_id,
            )
        )
