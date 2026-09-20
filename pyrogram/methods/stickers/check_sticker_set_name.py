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


class CheckStickerSetName:
    async def check_sticker_set_name(
        self: pyrogram.Client,
        short_name: str,
    ) -> bool:
        """Check if a sticker set short name is available.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            short_name (``str``):
                Short name to check.

        Returns:
            ``bool``: True if the short name is available, False otherwise.

        Example:
            .. code-block:: python

                # Check if short name is available
                is_available = await app.check_sticker_set_name("my_cool_pack")
        """
        return bool(
            await self.invoke(
                raw.functions.stickers.CheckShortName(
                    short_name=short_name,
                )
            )
        )
