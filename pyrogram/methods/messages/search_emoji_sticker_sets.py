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


class SearchEmojiStickerSets:
    async def search_emoji_sticker_sets(
        self: pyrogram.Client,
        query: str,
        hash: int = 0,
        exclude_featured: bool | None = None,
    ) -> raw.base.messages.FoundStickerSets:
        """Search for custom emoji sticker sets.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            query (``str``):
                The search query.

            hash (``int``, *optional*):
                Hash for caching.

            exclude_featured (``bool``, *optional*):
                If True, exclude featured sticker sets from results.

        Returns:
            :obj:`~pyrogram.raw.base.messages.FoundStickerSets`: The found sticker sets.

        Example:
            .. code-block:: python

                results = await app.search_emoji_sticker_sets("animated")
        """
        return await self.invoke(
            raw.functions.messages.SearchEmojiStickerSets(
                q=query,
                hash=hash,
                exclude_featured=exclude_featured,
            )
        )
