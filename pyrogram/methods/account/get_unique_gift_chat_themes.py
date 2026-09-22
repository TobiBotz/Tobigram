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


class GetUniqueGiftChatThemes:
    async def get_unique_gift_chat_themes(
        self: pyrogram.Client,
        limit: int,
        offset: str = "",
        hash: int = 0,
    ) -> raw.base.account.ChatThemes:
        """Obtain all chat themes associated to owned or hosted collectible gifts.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            limit (``int``):
                Maximum number of results to return.

            offset (``str``, *optional*):
                Offset for pagination, defaults to empty string.

            hash (``int``, *optional*):
                Hash used for caching, defaults to 0.

        Returns:
            :obj:`~pyrogram.raw.base.account.ChatThemes`: On success, chat themes are returned.
        """
        return await self.invoke(
            raw.functions.account.GetUniqueGiftChatThemes(
                offset=offset,
                limit=limit,
                hash=hash,
            )
        )
