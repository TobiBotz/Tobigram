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
from .resolve import resolve_stickerset


class SetStickerSetTitle:
    async def set_sticker_set_title(
        self: pyrogram.Client,
        short_name: str | types.StickerSet | raw.base.InputStickerSet,
        title: str,
    ) -> types.StickerSet:
        """Set the title of an existing sticker set created by you or your bot.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            short_name (``str`` | :obj:`~pyrogram.types.StickerSet`):
                Short name or StickerSet object of the sticker set to rename.

            title (``str``):
                New title for the sticker set, 1-64 characters.

        Returns:
            :obj:`~pyrogram.types.StickerSet`: On success, the updated sticker set is returned.

        Example:
            .. code-block:: python

                # Set title of a sticker set
                await app.set_sticker_set_title("mypack_by_bot", "New Title")
        """
        stickerset = resolve_stickerset(short_name)

        r = await self.invoke(
            raw.functions.stickers.RenameStickerSet(
                stickerset=stickerset,
                title=title,
            )
        )

        return await types.StickerSet._parse(self, r)
