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
from .resolve import resolve_sticker_doc


class SetStickerEmojiList:
    async def set_sticker_emoji_list(
        self: pyrogram.Client,
        sticker: str | types.Sticker | raw.base.InputDocument,
        emoji_list: list[str] | str,
    ) -> types.StickerSet:
        """Use this method to change the list of emoji assigned to a regular or custom emoji sticker.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            sticker (``str`` | :obj:`~pyrogram.types.Sticker` | :obj:`~pyrogram.raw.base.InputDocument`):
                File identifier or document of the sticker.

            emoji_list (List of ``str`` | ``str``):
                List of 1-20 emoji associated with the sticker or concatenated emoji string.

        Returns:
            :obj:`~pyrogram.types.StickerSet`: An updated sticker set is returned.

        Example:
            .. code-block:: python

                await app.set_sticker_emoji_list(sticker, ["🎉", "🥳"])
        """
        if isinstance(emoji_list, list):
            emoji_str = "".join(emoji_list)
        else:
            emoji_str = emoji_list or ""

        doc = await resolve_sticker_doc(self, sticker)

        r = await self.invoke(
            raw.functions.stickers.ChangeSticker(
                sticker=doc,
                emoji=emoji_str,
            )
        )

        return await types.StickerSet._parse(self, r)
