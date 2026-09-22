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


class SaveRecentSticker:
    async def save_recent_sticker(
        self: pyrogram.Client,
        sticker: raw.base.InputDocument,
        attached: bool | None = None,
        unsave: bool | None = None,
    ) -> bool:
        """Save or remove a sticker from recently used stickers.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            sticker (:obj:`~pyrogram.raw.base.InputDocument`):
                The sticker to save or unsave.

            attached (``bool``, *optional*):
                If True, work with stickers attached to photo/video files.

            unsave (``bool``, *optional*):
                If True, remove the sticker from recent stickers.

        Returns:
            ``bool``: True on success.

        Example:
            .. code-block:: python

                await app.save_recent_sticker(sticker)
        """
        return await self.invoke(
            raw.functions.messages.SaveRecentSticker(
                id=sticker,
                attached=attached,
                unsave=unsave,
            )
        )
