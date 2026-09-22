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


class GetSavedHistory:
    async def get_saved_history(
        self: pyrogram.Client,
        parent_peer: int | str,
        peer: int | str,
        offset_id: int = 0,
        offset_date: int = 0,
        add_offset: int = 0,
        limit: int = 100,
        max_id: int = 0,
        min_id: int = 0,
        hash: int = 0,
    ) -> raw.base.messages.Messages:
        """Get saved messages history for a specific peer.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            parent_peer (``int`` | ``str``):
                The parent peer (usually "me").

            peer (``int`` | ``str``):
                The peer whose saved messages to retrieve.

            offset_id (``int``, *optional*):
                Only return messages starting from the specified id.

            offset_date (``int``, *optional*):
                Only return messages starting from the specified date.

            add_offset (``int``, *optional*):
                Number of list elements to skip.

            limit (``int``, *optional*):
                Number of results to return. Defaults to 100.

            max_id (``int``, *optional*):
                If positive, the server will return only messages with IDs less than max_id.

            min_id (``int``, *optional*):
                If positive, only messages with IDs bigger than min_id will be returned.

            hash (``int``, *optional*):
                Hash for caching.

        Returns:
            :obj:`~pyrogram.raw.base.messages.Messages`: The messages object.

        Example:
            .. code-block:: python

                history = await app.get_saved_history("me", user_id)
        """
        parent = await self.resolve_peer(parent_peer)
        saved_peer = await self.resolve_peer(peer)

        return await self.invoke(
            raw.functions.messages.GetSavedHistory(
                parent_peer=parent,
                peer=saved_peer,
                offset_id=offset_id,
                offset_date=offset_date,
                add_offset=add_offset,
                limit=limit,
                max_id=max_id,
                min_id=min_id,
                hash=hash,
            )
        )
