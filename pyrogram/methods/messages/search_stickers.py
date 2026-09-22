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


class SearchStickers:
    async def search_stickers(
        self: pyrogram.Client,
        query: str,
        emoticon: str | None = None,
        lang_code: list[str] | None = None,
        offset: str = "",
        limit: int = 100,
        hash: int = 0,
        emojis: bool | None = None,
    ) -> raw.base.messages.FoundStickers:
        """Search for stickers by keyword or emoticon.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            query (``str``):
                The search query.

            emoticon (``str``, *optional*):
                Filter by associated emoji.

            lang_code (List of ``str``, *optional*):
                Language codes for the search.

            offset (``str``, *optional*):
                Pagination offset.

            limit (``int``, *optional*):
                Maximum number of results. Defaults to 100.

            hash (``int``, *optional*):
                Hash for caching.

            emojis (``bool``, *optional*):
                If True, search for custom emoji stickers.

        Returns:
            :obj:`~pyrogram.raw.base.messages.FoundStickers`: The found stickers.

        Example:
            .. code-block:: python

                results = await app.search_stickers("cat")
        """
        return await self.invoke(
            raw.functions.messages.SearchStickers(
                q=query,
                emoticon=emoticon,
                lang_code=lang_code or [],
                offset=offset,
                limit=limit,
                hash=hash,
                emojis=emojis,
            )
        )
