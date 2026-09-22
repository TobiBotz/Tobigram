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


class GetSearchResultsPositions:
    async def get_search_results_positions(
        self: pyrogram.Client,
        chat_id: int | str,
        filter: raw.base.MessagesFilter,
        offset_id: int = 0,
        limit: int = 100,
        saved_peer_id: int | str | None = None,
    ) -> raw.base.messages.SearchResultsPositions:
        """Get positions of search results within a chat history.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            filter (:obj:`~pyrogram.raw.base.MessagesFilter`):
                The filter to search with.

            offset_id (``int``, *optional*):
                Only return messages starting from the specified id.

            limit (``int``, *optional*):
                Maximum number of results. Defaults to 100.

            saved_peer_id (``int`` | ``str``, *optional*):
                Peer for saved messages context.

        Returns:
            :obj:`~pyrogram.raw.base.messages.SearchResultsPositions`: The positions of search results.

        Example:
            .. code-block:: python

                positions = await app.get_search_results_positions(
                    chat_id, raw.types.InputMessagesFilterVideo()
                )
        """
        peer = await self.resolve_peer(chat_id)
        saved = await self.resolve_peer(saved_peer_id) if saved_peer_id else None

        return await self.invoke(
            raw.functions.messages.GetSearchResultsPositions(
                peer=peer,
                filter=filter,
                offset_id=offset_id,
                limit=limit,
                saved_peer_id=saved,
            )
        )
