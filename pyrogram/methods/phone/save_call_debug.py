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


class SaveCallDebug:
    async def save_call_debug(
        self: pyrogram.Client,
        call_id: int,
        access_hash: int,
        debug: str | raw.base.DataJSON,
    ) -> bool:
        """Send phone call debug statistics to Telegram servers.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            call_id (``int``):
                The unique phone call ID.

            access_hash (``int``):
                The access hash of the phone call.

            debug (``str`` | :obj:`~pyrogram.raw.base.DataJSON`):
                Debug statistics JSON string or DataJSON object.

        Returns:
            ``bool``: On success, True is returned.

        Example:
            .. code-block:: python

                await app.save_call_debug(call_id=123, access_hash=456, debug='{"packets_lost": 0}')
        """
        if isinstance(debug, str):
            debug = raw.types.DataJSON(data=debug)

        return await self.invoke(
            raw.functions.phone.SaveCallDebug(
                peer=raw.types.InputPhoneCall(id=call_id, access_hash=access_hash),
                debug=debug,
            )
        )
