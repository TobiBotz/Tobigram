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


class InvokeWebViewCustomMethod:
    async def invoke_web_view_custom_method(
        self: pyrogram.Client,
        bot: int | str,
        custom_method: str,
        params: str | raw.base.DataJSON,
    ) -> raw.base.DataJSON:
        """Send a custom request from a Mini Bot App.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            bot (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target bot.

            custom_method (``str``):
                Identifier of the custom method to invoke.

            params (``str`` | :obj:`~pyrogram.raw.base.DataJSON`):
                JSON-serialized parameters or a DataJSON object.

        Returns:
            :obj:`~pyrogram.raw.base.DataJSON`: JSON-serialized response from Telegram.

        Example:
            .. code-block:: python

                res = await app.invoke_web_view_custom_method("my_bot", "custom_func", '{"key": "value"}')
        """
        if isinstance(params, str):
            params = raw.types.DataJSON(data=params)

        return await self.invoke(
            raw.functions.bots.InvokeWebViewCustomMethod(
                bot=await self.resolve_peer(bot),
                custom_method=custom_method,
                params=params,
            )
        )
