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


class ToggleStickerSets:
    async def toggle_sticker_sets(
        self: pyrogram.Client,
        sticker_sets: list[raw.base.InputStickerSet],
        uninstall: bool | None = None,
        archive: bool | None = None,
        unarchive: bool | None = None,
    ) -> bool:
        """Install, uninstall, archive or unarchive multiple sticker sets at once.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            sticker_sets (List of :obj:`~pyrogram.raw.base.InputStickerSet`):
                The sticker sets to toggle.

            uninstall (``bool``, *optional*):
                If True, uninstall the sticker sets.

            archive (``bool``, *optional*):
                If True, archive the sticker sets.

            unarchive (``bool``, *optional*):
                If True, unarchive the sticker sets.

        Returns:
            ``bool``: True on success.

        Example:
            .. code-block:: python

                await app.toggle_sticker_sets(sticker_sets, archive=True)
        """
        return await self.invoke(
            raw.functions.messages.ToggleStickerSets(
                stickersets=sticker_sets,
                uninstall=uninstall,
                archive=archive,
                unarchive=unarchive,
            )
        )
