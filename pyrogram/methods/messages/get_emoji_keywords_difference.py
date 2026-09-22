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


class GetEmojiKeywordsDifference:
    async def get_emoji_keywords_difference(
        self: pyrogram.Client,
        lang_code: str,
        from_version: int,
    ) -> raw.base.EmojiKeywordsDifference:
        """Get emoji keywords difference (updates) for a given language.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            lang_code (``str``):
                The language code (e.g., "en", "ru").

            from_version (``int``):
                The current version of the emoji keywords to get updates from.

        Returns:
            :obj:`~pyrogram.raw.base.EmojiKeywordsDifference`: The emoji keywords difference.

        Example:
            .. code-block:: python

                diff = await app.get_emoji_keywords_difference("en", from_version=5)
        """
        return await self.invoke(
            raw.functions.messages.GetEmojiKeywordsDifference(
                lang_code=lang_code,
                from_version=from_version,
            )
        )
