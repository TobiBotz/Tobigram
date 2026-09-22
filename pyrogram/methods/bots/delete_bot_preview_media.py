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


class DeleteBotPreviewMedia:
    async def delete_bot_preview_media(
        self: pyrogram.Client,
        bot: int | str,
        lang_code: str,
        media: list[raw.base.InputMedia],
    ) -> bool:
        """Delete Main Mini App previews for a bot.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            bot (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target bot.

            lang_code (``str``):
                ISO 639-1 language code, indicating the localization of the preview to delete.

            media (List of :obj:`~pyrogram.raw.base.InputMedia`):
                The photo/video previews to delete.

        Returns:
            ``bool``: On success, True is returned.

        Example:
            .. code-block:: python

                await app.delete_bot_preview_media("my_bot", "en", [media1, media2])
        """
        return await self.invoke(
            raw.functions.bots.DeletePreviewMedia(
                bot=await self.resolve_peer(bot),
                lang_code=lang_code,
                media=media,
            )
        )
