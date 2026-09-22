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


class SearchSentMedia:
    async def search_sent_media(
        self: pyrogram.Client,
        query: str,
        filter: raw.base.MessagesFilter,
        limit: int = 100,
    ) -> raw.base.messages.Messages:
        """Search for media sent by the current user.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            query (``str``):
                The search query.

            filter (:obj:`~pyrogram.raw.base.MessagesFilter`):
                The media type filter.

            limit (``int``, *optional*):
                Maximum number of results. Defaults to 100.

        Returns:
            :obj:`~pyrogram.raw.base.messages.Messages`: The found messages.

        Example:
            .. code-block:: python

                results = await app.search_sent_media(
                    "photo", raw.types.InputMessagesFilterPhotos()
                )
        """
        return await self.invoke(
            raw.functions.messages.SearchSentMedia(q=query, filter=filter, limit=limit)
        )
