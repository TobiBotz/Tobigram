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
from pyrogram import raw, utils


class GetUserInfo:
    async def get_user_info(
        self: pyrogram.Client,
        user_id: int | str,
    ) -> raw.base.help.UserInfo:
        """Get internal user info (can only be used by TSF members).

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            user_id (``int`` | ``str``):
                User ID.

        Returns:
            :obj:`~pyrogram.raw.base.help.UserInfo`: The user info.

        Example:
            .. code-block:: python

                info = await app.get_user_info(user_id)
        """
        return await self.invoke(
            raw.functions.help.GetUserInfo(
                user_id=utils.get_input_user(await self.resolve_peer(user_id)),
            )
        )
