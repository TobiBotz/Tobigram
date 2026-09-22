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


class SendCustomRequest:
    async def send_custom_request(
        self: pyrogram.Client,
        custom_method: str,
        params: str | raw.base.DataJSON,
    ) -> raw.base.DataJSON:
        """Send a custom request (for bots).

        .. include:: /_includes/usable-by/bots.rst

        Parameters:
            custom_method (``str``):
                The custom method name.

            params (``str`` | :obj:`~pyrogram.raw.base.DataJSON`):
                JSON-serialized method parameters or a DataJSON object.

        Returns:
            :obj:`~pyrogram.raw.base.DataJSON`: JSON-serialized response from Telegram.

        Example:
            .. code-block:: python

                res = await bot.send_custom_request("myCustomMethod", '{"foo": "bar"}')
        """
        if isinstance(params, str):
            params = raw.types.DataJSON(data=params)

        return await self.invoke(
            raw.functions.bots.SendCustomRequest(
                custom_method=custom_method,
                params=params,
            )
        )
