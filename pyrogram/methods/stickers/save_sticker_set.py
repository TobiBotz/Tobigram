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
from .resolve import resolve_stickerset


class SaveStickerSet:
    async def save_sticker_set(
        self: pyrogram.Client,
        short_name: str | types.StickerSet | raw.base.InputStickerSet,
        *,
        archived: bool = False,
    ) -> bool:
        """Save (install) a sticker set to your account's stickers.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            short_name (``str`` | :obj:`~pyrogram.types.StickerSet` | :obj:`~pyrogram.raw.base.InputStickerSet`):
                Short name or StickerSet object of the sticker set to save.

            archived (``bool``, *optional*):
                Whether to save the sticker set directly to archives.
                Defaults to False.

        Returns:
            ``bool``: On success, True is returned.

        Example:
            .. code-block:: python

                # Save a sticker set to your account
                await app.save_sticker_set("animals")
        """
        stickerset = resolve_stickerset(short_name)

        r = await self.invoke(
            raw.functions.messages.InstallStickerSet(
                stickerset=stickerset,
                archived=archived,
            )
        )

        return isinstance(
            r,
            (
                raw.types.messages.StickerSetInstallResultSuccess,
                raw.types.messages.StickerSetInstallResultArchive,
            ),
        )
