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


class ReorderStickerSets:
    async def reorder_sticker_sets(
        self: pyrogram.Client,
        order: list[int],
        masks: bool | None = None,
        emojis: bool | None = None,
    ) -> bool:
        """Reorder installed sticker sets.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            order (List of ``int``):
                The new order of sticker set IDs.

            masks (``bool``, *optional*):
                If True, reorder mask sticker sets.

            emojis (``bool``, *optional*):
                If True, reorder custom emoji sticker sets.

        Returns:
            ``bool``: True on success.

        Example:
            .. code-block:: python

                await app.reorder_sticker_sets([111, 222, 333])
        """
        return await self.invoke(
            raw.functions.messages.ReorderStickerSets(
                order=order,
                masks=masks,
                emojis=emojis,
            )
        )
