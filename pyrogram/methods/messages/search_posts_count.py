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


import pyrogram
from pyrogram import raw


class SearchPostsCount:
    async def search_posts_count(
        self: "pyrogram.Client", hashtag: str | None = None, query: str | None = None
    ) -> int:
        """Get the number of public posts matching a hashtag or a text search.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            hashtag (``str``, *optional*):
                Hashtag to search for, with or without the leading "#".

            query (``str``, *optional*):
                Text to search for instead of a hashtag.
                Searching by text requires a Premium account; Telegram answers
                ``[403 PREMIUM_ACCOUNT_REQUIRED]`` otherwise.

        Returns:
            ``int``: On success, the posts count is returned.

        Raises:
            ValueError: In case neither *hashtag* nor *query* is given.

        Example:
            .. code-block:: python

                count = await app.search_posts_count("wzgram")
        """
        if hashtag is None and query is None:
            raise ValueError("You must pass either hashtag or query")

        r = await self.invoke(
            raw.functions.channels.SearchPosts(
                hashtag=hashtag.lstrip("#") if hashtag is not None else None,
                query=query,
                offset_rate=0,
                offset_peer=raw.types.InputPeerEmpty(),
                offset_id=0,
                limit=1,
            )
        )

        return getattr(r, "count", len(r.messages))
