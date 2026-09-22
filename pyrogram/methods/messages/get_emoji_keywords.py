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


class GetEmojiKeywords:
    async def get_emoji_keywords(
        self: pyrogram.Client,
        lang_code: str,
    ) -> raw.base.EmojiKeywordsDifference:
        """Get emoji keywords for a given language.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            lang_code (``str``):
                The language code (e.g., "en", "ru").

        Returns:
            :obj:`~pyrogram.raw.base.EmojiKeywordsDifference`: The emoji keywords.

        Example:
            .. code-block:: python

                keywords = await app.get_emoji_keywords("en")
        """
        return await self.invoke(raw.functions.messages.GetEmojiKeywords(lang_code=lang_code))
