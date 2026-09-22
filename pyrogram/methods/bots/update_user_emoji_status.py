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


class UpdateUserEmojiStatus:
    async def update_user_emoji_status(
        self: pyrogram.Client,
        user_id: int | str,
        emoji_status: raw.base.EmojiStatus,
    ) -> bool:
        """Change the emoji status of a user (for bots).

        .. include:: /_includes/usable-by/bots.rst

        Parameters:
            user_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target user.

            emoji_status (:obj:`~pyrogram.raw.base.EmojiStatus`):
                The emoji status to set.

        Returns:
            ``bool``: On success, True is returned.

        Example:
            .. code-block:: python

                from pyrogram import raw

                await bot.update_user_emoji_status(
                    user_id=12345,
                    emoji_status=raw.types.EmojiStatus(document_id=12345678)
                )
        """
        return await self.invoke(
            raw.functions.bots.UpdateUserEmojiStatus(
                user_id=await self.resolve_peer(user_id),
                emoji_status=emoji_status,
            )
        )
