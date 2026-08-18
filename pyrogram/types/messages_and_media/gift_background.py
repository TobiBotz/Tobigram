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

from typing import Optional

from pyrogram import raw

from ..object import Object


class GiftBackground(Object):
    """The background a gift is shown on.

    Parameters:
        center_color (``int``, *optional*):
            Center color of the background in RGB format.

        edge_color (``int``, *optional*):
            Edge color of the background in RGB format.

        text_color (``int``, *optional*):
            Text color of the background in RGB format.
    """

    def __init__(
        self,
        *,
        center_color: Optional[int] = None,
        edge_color: Optional[int] = None,
        text_color: Optional[int] = None
    ):
        super().__init__()

        self.center_color = center_color
        self.edge_color = edge_color
        self.text_color = text_color

    @staticmethod
    def _parse(
        background: "raw.base.StarGiftBackground"
    ) -> Optional["GiftBackground"]:
        if not isinstance(background, raw.types.StarGiftBackground):
            return None

        return GiftBackground(
            center_color=background.center_color,
            edge_color=background.edge_color,
            text_color=background.text_color
        )
