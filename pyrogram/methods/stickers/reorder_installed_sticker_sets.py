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

from collections.abc import Iterable

import pyrogram
from pyrogram import raw, types
from .resolve import resolve_stickerset


class ReorderInstalledStickerSets:
    async def reorder_installed_sticker_sets(
        self: pyrogram.Client,
        order: Iterable[str | types.StickerSet | raw.base.InputStickerSet],
        masks: bool = False,
        emojis: bool = False,
    ) -> bool:
        """Reorder installed sticker sets.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            order (Iterable of ``str`` | :obj:`~pyrogram.types.StickerSet`):
                List of short names or StickerSet objects in new order.

            masks (``bool``, *optional*):
                Pass True to reorder mask sticker sets.

            emojis (``bool``, *optional*):
                Pass True to reorder custom emoji sticker sets.

        Returns:
            ``bool``: True on success.

        Example:
            .. code-block:: python

                await app.reorder_installed_sticker_sets(["pack1", "pack2"])
        """
        order_sets = [resolve_stickerset(s) for s in order]

        return await self.invoke(
            raw.functions.messages.ReorderStickerSets(
                order=order_sets,
                masks=masks or None,
                emojis=emojis or None,
            )
        )
