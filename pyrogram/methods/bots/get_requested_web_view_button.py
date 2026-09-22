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


class GetRequestedWebViewButton:
    async def get_requested_web_view_button(
        self: pyrogram.Client,
        bot: int | str,
        webapp_req_id: str,
    ) -> raw.base.KeyboardButton:
        """Fetch the peer request button a bot prepared for a Mini App.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            bot (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target bot.

            webapp_req_id (``str``):
                The Mini App request ID from the web_app_request_chat event req_id.

        Returns:
            :obj:`~pyrogram.raw.base.KeyboardButton`: The prepared keyboard button.

        Example:
            .. code-block:: python

                button = await app.get_requested_web_view_button("my_bot", "req_123")
        """
        return await self.invoke(
            raw.functions.bots.GetRequestedWebViewButton(
                bot=await self.resolve_peer(bot),
                webapp_req_id=webapp_req_id,
            )
        )
