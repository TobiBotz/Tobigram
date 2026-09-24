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


class ChangeStickerSet:
    async def change_sticker_set(
        self: pyrogram.Client, name: str, is_installed: bool, is_archived: bool | None = None
    ) -> bool:
        """Install, uninstall, archive or unarchive a sticker set.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            name (``str``):
                Name of the sticker set.

            is_installed (``bool``):
                Pass True to install the sticker set, False to uninstall it.

            is_archived (``bool``, *optional*):
                Pass True to archive the installed sticker set.

        Returns:
            ``bool``: True, on success.

        Example:
            .. code-block:: python

                await app.change_sticker_set("animals", is_installed=True)
        """
        if is_installed:
            r = await self.invoke(
                raw.functions.messages.InstallStickerSet(
                    stickerset=raw.types.InputStickerSetShortName(short_name=name),
                    archived=bool(is_archived),
                )
            )
        else:
            r = await self.invoke(
                raw.functions.messages.UninstallStickerSet(
                    stickerset=raw.types.InputStickerSetShortName(short_name=name)
                )
            )

        return bool(r)
