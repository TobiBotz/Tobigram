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


class GetFeaturedEmojiStickers:
    async def get_featured_emoji_stickers(
        self: pyrogram.Client,
        hash: int = 0,
    ) -> raw.base.messages.FeaturedStickers:
        """Get featured/trending custom emoji sticker sets.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            hash (``int``, *optional*):
                Hash for caching, for more info click `here <https://core.telegram.org/api/offsets#hash-generation>`_.

        Returns:
            :obj:`~pyrogram.raw.base.messages.FeaturedStickers`: The featured emoji sticker sets.

        Example:
            .. code-block:: python

                featured = await app.get_featured_emoji_stickers()
        """
        return await self.invoke(raw.functions.messages.GetFeaturedEmojiStickers(hash=hash))
