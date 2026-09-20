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

from pyrogram import raw
from ..object import Object

if TYPE_CHECKING:
    from pyrogram import types


class InputSticker(Object):
    """A sticker to be added to a sticker set.

    Parameters:
        sticker (``str`` | ``BinaryIO`` | :obj:`~pyrogram.raw.base.InputDocument`):
            Sticker file.
            Pass a file_id as string to use a file that exists on Telegram servers,
            pass a file path as string to upload a new file that exists on your local machine,
            pass a binary file-like object with its attribute ".name" set for in-memory uploads, or
            pass a raw :obj:`~pyrogram.raw.base.InputDocument`.

        emoji (``str``, *optional*):
            One or more emoji associated with the sticker.
            Defaults to "😀".

        keywords (``str``, *optional*):
            List of 0-20 search keywords for the sticker with total length of up to 64 characters,
            separated by commas.

        mask_coords (:obj:`~pyrogram.types.MaskPosition` | :obj:`~pyrogram.raw.types.MaskCoords`, *optional*):
            Position where the mask should be placed on faces (for mask sticker sets only).
    """

    def __init__(
        self,
        sticker: str | BinaryIO | types.Sticker | raw.base.InputDocument,
        emoji: str | None = None,
        keywords: str | None = None,
        mask_coords: types.MaskPosition | raw.types.MaskCoords | None = None,
    ) -> None:
        super().__init__()

        if emoji is None and hasattr(sticker, "emoji") and getattr(sticker, "emoji"):
            emoji = getattr(sticker, "emoji")

        self.sticker = sticker
        self.emoji = emoji or "😀"
        self.keywords = keywords
        self.mask_coords = mask_coords
