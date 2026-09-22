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


class SendWebViewData:
    async def send_web_view_data(
        self: pyrogram.Client,
        bot_id: int | str,
        button_text: str,
        data: str,
        random_id: int | None = None,
    ) -> raw.base.Updates:
        """Send data from a web app button to a bot.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            bot_id (``int`` | ``str``):
                The bot to send data to.

            button_text (``str``):
                The text of the button that was clicked.

            data (``str``):
                The data to send to the bot.

            random_id (``int``, *optional*):
                Random ID for deduplication.

        Returns:
            :obj:`~pyrogram.raw.base.Updates`: The updates object.

        Example:
            .. code-block:: python

                await app.send_web_view_data(bot_id, "Submit", '{"key": "value"}')
        """
        import random

        bot = await self.resolve_peer(bot_id)

        return await self.invoke(
            raw.functions.messages.SendWebViewData(
                bot=bot,
                random_id=random_id or random.randint(0, 2**31),
                button_text=button_text,
                data=data,
            )
        )
