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


class SearchStories:
    async def search_stories(
        self: pyrogram.Client,
        hashtag: str | None = None,
        chat_id: int | str | None = None,
        offset: str = "",
        limit: int = 100,
        area: raw.base.MediaArea | None = None,
    ) -> raw.types.stories.FoundStories:
        """Search public stories by hashtag, location area, or chat.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            hashtag (``str``, *optional*):
                The hashtag to search for.

            chat_id (``int`` | ``str``, *optional*):
                Target chat to limit the search to.

            offset (``str``, *optional*):
                Pagination offset. Defaults to empty string.

            limit (``int``, *optional*):
                Number of stories to return. Defaults to 100.

            area (:obj:`~pyrogram.raw.base.MediaArea`, *optional*):
                Media area / location to search stories for.

        Returns:
            :obj:`~pyrogram.raw.types.stories.FoundStories`: On success, found stories object is returned.

        Example:
            .. code-block:: python

                stories = await app.search_stories(hashtag="travel")
        """
        peer = await self.resolve_peer(chat_id) if chat_id else None

        return await self.invoke(
            raw.functions.stories.SearchPosts(
                hashtag=hashtag,
                peer=peer,
                offset=offset,
                limit=limit,
                area=area,
            )
        )
