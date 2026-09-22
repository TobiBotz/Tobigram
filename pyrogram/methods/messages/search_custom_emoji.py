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


class SearchCustomEmoji:
    async def search_custom_emoji(
        self: pyrogram.Client,
        emoticon: str,
        hash: int = 0,
    ) -> raw.base.EmojiList:
        """Search for custom emoji by emoticon text.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            emoticon (``str``):
                The emoji character(s) to search for.

            hash (``int``, *optional*):
                Hash for caching.

        Returns:
            :obj:`~pyrogram.raw.base.EmojiList`: The list of custom emoji.

        Example:
            .. code-block:: python

                results = await app.search_custom_emoji("😀")
        """
        return await self.invoke(
            raw.functions.messages.SearchCustomEmoji(emoticon=emoticon, hash=hash)
        )
