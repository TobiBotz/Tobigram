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
from pyrogram import raw, types


class GetForumTopicIconStickers:
    async def get_forum_topic_icon_stickers(
        self: pyrogram.Client,
    ) -> list[types.Sticker]:
        """Get custom emoji stickers, which can be used as a forum topic icon by any user.

        .. include:: /_includes/usable-by/users-bots.rst

        Returns:
            List of :obj:`~pyrogram.types.Sticker`: On success, a list of stickers is returned.

        Example:
            .. code-block:: python

                stickers = await app.get_forum_topic_icon_stickers()
                for sticker in stickers:
                    print(sticker.file_id)
        """
        r = await self.invoke(
            raw.functions.messages.GetStickerSet(
                stickerset=raw.types.InputStickerSetEmojiDefaultTopicIcons(),
                hash=0,
            )
        )

        sticker_set = await types.StickerSet._parse(self, r)
        return sticker_set.stickers if sticker_set else []
