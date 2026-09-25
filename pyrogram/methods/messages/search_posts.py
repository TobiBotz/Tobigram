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
from pyrogram import raw, types, utils
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator


class SearchPosts:
    async def search_posts(
        self: pyrogram.Client,
        hashtag: str | None = None,
        query: str | None = None,
        limit: int = 0,
    ) -> AsyncGenerator[types.Message, None]:
        """Search public posts by hashtag or by text.

        If you want to get the posts count only, see :meth:`~pyrogram.Client.search_posts_count`.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            hashtag (``str``, *optional*):
                Hashtag to search for, with or without the leading ``#``.

            query (``str``, *optional*):
                Text to search for instead of a hashtag.
                Searching by text requires a Premium account; Telegram answers
                ``[403 PREMIUM_ACCOUNT_REQUIRED]`` otherwise.

            limit (``int``, *optional*):
                Limits the number of posts to be retrieved.
                By default, no limit is applied and all posts are returned.

        Returns:
            ``Generator``: A generator yielding :obj:`~pyrogram.types.Message` objects.

        Raises:
            ValueError: In case neither *hashtag* nor *query* is given.

        Example:
            .. code-block:: python

                # Search for posts with a hashtag
                async for post in app.search_posts(hashtag="news", limit=20):
                    print(post.chat.title, post.text)

                # Search for posts mentioning "telegram" (Premium only)
                async for post in app.search_posts(query="telegram", limit=50):
                    print(post.chat.title, post.text)
        """
        if hashtag is None and query is None:
            raise ValueError("You must pass either hashtag or query")

        current = 0
        total = abs(limit) or (1 << 31) - 1
        sub_limit = min(100, total)

        offset_rate = 0
        offset_peer = raw.types.InputPeerEmpty()
        offset_id = 0

        while True:
            r = await self.invoke(
                raw.functions.channels.SearchPosts(
                    hashtag=hashtag.lstrip("#") if hashtag is not None else None,
                    query=query,
                    offset_rate=offset_rate,
                    offset_peer=offset_peer,
                    offset_id=offset_id,
                    limit=sub_limit,
                ),
                sleep_threshold=60,
            )

            messages = await utils.parse_messages(self, r, replies=0)

            if not messages:
                return

            last = messages[-1]
            offset_rate = getattr(r, "next_rate", 0) or 0
            offset_peer = await self.resolve_peer(last.chat.id)
            offset_id = last.id

            for message in messages:
                yield message

                current += 1

                if current >= total:
                    return
