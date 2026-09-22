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


class GetBotPreviewInfo:
    async def get_bot_preview_info(
        self: pyrogram.Client,
        bot: int | str,
        lang_code: str,
    ) -> raw.base.bots.PreviewInfo:
        """Fetch Main Mini App preview information for a bot.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            bot (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target bot.

            lang_code (``str``):
                Fetch previews for the specified ISO 639-1 language code.

        Returns:
            :obj:`~pyrogram.raw.base.bots.PreviewInfo`: The bot preview information.

        Example:
            .. code-block:: python

                info = await app.get_bot_preview_info("my_bot", "en")
        """
        return await self.invoke(
            raw.functions.bots.GetPreviewInfo(
                bot=await self.resolve_peer(bot),
                lang_code=lang_code,
            )
        )
