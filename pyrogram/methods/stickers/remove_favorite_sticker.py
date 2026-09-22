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


class RemoveFavoriteSticker:
    async def remove_favorite_sticker(
        self: pyrogram.Client,
        sticker: str | types.Sticker | types.Message | raw.base.InputDocument,
    ) -> bool:
        """Remove a sticker from favourites.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            sticker (``str`` | :obj:`~pyrogram.types.Sticker` | :obj:`~pyrogram.types.Message` | :obj:`~pyrogram.raw.base.InputDocument`):
                The sticker to remove from favourites.

        Returns:
            ``bool``: True on success.

        Example:
            .. code-block:: python

                await app.remove_favorite_sticker(sticker)
        """
        if isinstance(sticker, types.Message) and sticker.sticker:
            sticker = sticker.sticker

        doc = (
            await resolve_sticker_doc(self, sticker)
            if not isinstance(sticker, raw.base.InputDocument)
            else sticker
        )
        return await self.invoke(raw.functions.messages.FaveSticker(id=doc, unfave=True))
