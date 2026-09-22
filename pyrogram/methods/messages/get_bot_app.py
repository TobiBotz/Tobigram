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


class GetBotApp:
    async def get_bot_app(
        self: pyrogram.Client,
        app: raw.base.InputBotApp,
        hash: int = 0,
    ) -> raw.base.messages.BotApp:
        """Get information about a bot web app.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            app (:obj:`~pyrogram.raw.base.InputBotApp`):
                The bot app to get info for.

            hash (``int``, *optional*):
                Hash for caching.

        Returns:
            :obj:`~pyrogram.raw.base.messages.BotApp`: The bot app info.

        Example:
            .. code-block:: python

                info = await app.get_bot_app(raw.types.InputBotAppShortName(bot=bot, short_name="myapp"))
        """
        return await self.invoke(raw.functions.messages.GetBotApp(app=app, hash=hash))
