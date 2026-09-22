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

from typing import TYPE_CHECKING, BinaryIO

from pyrogram import enums, raw
from ..object import Object

if TYPE_CHECKING:
    from pyrogram import types


class InputSticker(Object):
    """A sticker to be added to a sticker set.

    Parameters:
        sticker (``str`` | ``BinaryIO`` | :obj:`~pyrogram.types.Sticker` | :obj:`~pyrogram.raw.base.InputDocument`):
            Sticker file.
            Pass a file_id as string to use a file that exists on Telegram servers,
            pass a file path as string to upload a new file that exists on your local machine,
            pass a binary file-like object with its attribute ".name" set for in-memory uploads, or
            pass a raw :obj:`~pyrogram.raw.base.InputDocument`.

        emoji (``str``, *optional*):
            One or more emoji associated with the sticker.
            Defaults to "😀".

        keywords (List of ``str`` | ``str``, *optional*):
            List of 0-20 search keywords for the sticker with total length of up to 64 characters,
            or comma-separated keywords string.

        mask_coords (:obj:`~pyrogram.types.MaskPosition` | :obj:`~pyrogram.raw.types.MaskCoords`, *optional*):
            Position where the mask should be placed on faces (for mask sticker sets only).

        format (:obj:`~pyrogram.enums.StickerFormat`, *optional*):
            Format of the sticker (static, animated, or video).

        emoji_list (List of ``str``, *optional*):
            List of 1-20 emoji associated with the sticker.

        mask_position (:obj:`~pyrogram.types.MaskPosition`, *optional*):
            Position where the mask should be placed on faces (alias for mask_coords).
    """

    def __init__(
        self,
        sticker: str | BinaryIO | types.Sticker | raw.base.InputDocument,
        emoji: str | None = None,
        keywords: list[str] | str | None = None,
        mask_coords: types.MaskPosition | raw.types.MaskCoords | None = None,
        *,
        format: enums.StickerFormat | None = None,
        emoji_list: list[str] | str | None = None,
        mask_position: types.MaskPosition | raw.types.MaskCoords | None = None,
    ) -> None:
        super().__init__()

        em = emoji_list if emoji_list is not None else emoji
        if isinstance(em, list):
            em = "".join(em)
        elif em is None and hasattr(sticker, "emoji") and getattr(sticker, "emoji"):
            em = getattr(sticker, "emoji")

        kw = keywords
        if isinstance(kw, list):
            kw = ",".join(kw)

        mc = mask_position if mask_position is not None else mask_coords

        self.sticker = sticker
        self.emoji = em or "😀"
        self.emoji_list = [self.emoji] if em else ["😀"]
        self.keywords = kw
        self.mask_coords = mc
        self.mask_position = mc
        self.format = format
