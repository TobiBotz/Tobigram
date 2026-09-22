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


class SetChatWallPaper:
    async def set_chat_wallpaper(
        self: pyrogram.Client,
        chat_id: int | str,
        wallpaper: raw.base.InputWallPaper | None = None,
        settings: raw.base.WallPaperSettings | None = None,
        wallpaper_id: int | None = None,
        for_both: bool | None = None,
        revert: bool | None = None,
    ) -> raw.base.Updates:
        """Set a wallpaper for a chat.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            wallpaper (:obj:`~pyrogram.raw.base.InputWallPaper`, *optional*):
                The wallpaper to set.

            settings (:obj:`~pyrogram.raw.base.WallPaperSettings`, *optional*):
                Wallpaper settings.

            wallpaper_id (``int``, *optional*):
                ID of a previously set wallpaper to reuse.

            for_both (``bool``, *optional*):
                If True, set the wallpaper for both sides of the conversation.

            revert (``bool``, *optional*):
                If True, revert the wallpaper to default.

        Returns:
            :obj:`~pyrogram.raw.base.Updates`: The updates object.

        Example:
            .. code-block:: python

                await app.set_chat_wallpaper(chat_id, wallpaper=wp)
        """
        peer = await self.resolve_peer(chat_id)

        return await self.invoke(
            raw.functions.messages.SetChatWallPaper(
                peer=peer,
                wallpaper=wallpaper,
                settings=settings,
                id=wallpaper_id,
                for_both=for_both,
                revert=revert,
            )
        )
