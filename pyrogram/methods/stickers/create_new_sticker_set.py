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

from typing import BinaryIO

import pyrogram
from pyrogram import raw, types
from .resolve import resolve_sticker_item, resolve_thumb_doc


class CreateNewStickerSet:
    async def create_new_sticker_set(
        self: pyrogram.Client,
        user_id: int | str,
        title: str,
        short_name: str,
        stickers: list[types.InputSticker | str | BinaryIO | raw.base.InputDocument],
        *,
        default_emoji: str = "😀",
        masks: bool = False,
        emojis: bool = False,
        text_color: bool = False,
        thumb: str | BinaryIO | raw.base.InputDocument | None = None,
        software: str | None = None,
    ) -> types.StickerSet:
        """Create a new sticker set.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            user_id (``int`` | ``str``):
                User identifier or username of the sticker set owner.

            title (``str``):
                Sticker set title, 1-64 characters.

            short_name (``str``):
                Short name of sticker set.

            stickers (List of :obj:`~pyrogram.types.InputSticker` | ``str`` | ``BinaryIO``):
                List of stickers to add to the sticker set.

            default_emoji (``str``, *optional*):
                Default emoji to use if a sticker is passed without an associated emoji.

            masks (``bool``, *optional*):
                Pass True if this is a mask sticker set.

            emojis (``bool``, *optional*):
                Pass True if this is a custom emoji sticker set.

            text_color (``bool``, *optional*):
                Whether the color of TGS custom emojis should change to text color.

            thumb (``str`` | ``BinaryIO`` | :obj:`~pyrogram.raw.base.InputDocument`, *optional*):
                Thumbnail for the sticker set.

            software (``str``, *optional*):
                Name of the software used to create the stickers.

        Returns:
            :obj:`~pyrogram.types.StickerSet`: On success, the created sticker set is returned.

        Example:
            .. code-block:: python

                await app.create_new_sticker_set(
                    user_id="me",
                    title="My Pack",
                    short_name="mypack_by_bot",
                    stickers=[types.InputSticker("sticker1.webp", emoji="😀")]
                )
        """
        peer = await self.resolve_peer(user_id)

        sticker_items = [
            await resolve_sticker_item(self, item, default_emoji=default_emoji) for item in stickers
        ]

        thumb_doc = await resolve_thumb_doc(self, thumb)

        r = await self.invoke(
            raw.functions.stickers.CreateStickerSet(
                user_id=peer,
                title=title,
                short_name=short_name,
                stickers=sticker_items,
                masks=masks or None,
                emojis=emojis or None,
                text_color=text_color or None,
                thumb=thumb_doc,
                software=software,
            )
        )

        return await types.StickerSet._parse(self, r)
