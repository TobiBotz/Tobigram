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


class ReorderBotPreviewMedias:
    async def reorder_bot_preview_medias(
        self: pyrogram.Client,
        bot: int | str,
        lang_code: str,
        order: list[raw.base.InputMedia],
    ) -> bool:
        """Reorder Main Mini App previews for a bot.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            bot (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target bot.

            lang_code (``str``):
                ISO 639-1 language code, indicating the localization of the previews to reorder.

            order (List of :obj:`~pyrogram.raw.base.InputMedia`):
                New order of the previews.

        Returns:
            ``bool``: On success, True is returned.

        Example:
            .. code-block:: python

                await app.reorder_bot_preview_medias("my_bot", "en", [media2, media1])
        """
        return await self.invoke(
            raw.functions.bots.ReorderPreviewMedias(
                bot=await self.resolve_peer(bot),
                lang_code=lang_code,
                order=order,
            )
        )
