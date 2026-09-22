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


class EditBotPreviewMedia:
    async def edit_bot_preview_media(
        self: pyrogram.Client,
        bot: int | str,
        lang_code: str,
        media: raw.base.InputMedia,
        new_media: raw.base.InputMedia,
    ) -> raw.base.BotPreviewMedia:
        """Edit a Main Mini App preview for a bot.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            bot (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target bot.

            lang_code (``str``):
                ISO 639-1 language code, indicating the localization of the preview to edit.

            media (:obj:`~pyrogram.raw.base.InputMedia`):
                The photo/video preview to replace.

            new_media (:obj:`~pyrogram.raw.base.InputMedia`):
                The new photo/video preview.

        Returns:
            :obj:`~pyrogram.raw.base.BotPreviewMedia`: On success, the updated preview media is returned.

        Example:
            .. code-block:: python

                preview = await app.edit_bot_preview_media("my_bot", "en", old_media, new_media)
        """
        return await self.invoke(
            raw.functions.bots.EditPreviewMedia(
                bot=await self.resolve_peer(bot),
                lang_code=lang_code,
                media=media,
                new_media=new_media,
            )
        )
