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


class GetStarsGiftOptions:
    async def get_stars_gift_options(
        self: pyrogram.Client,
        user_id: int | str | None = None,
    ) -> list[raw.types.StarsGiftOption]:
        """Get available Telegram Stars gift packages for a user.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            user_id (``int`` | ``str``, *optional*):
                Target user ID or username.

        Returns:
            List of :obj:`~pyrogram.raw.types.StarsGiftOption`: On success, options are returned.

        Example:
            .. code-block:: python

                options = await app.get_stars_gift_options("user123")
        """
        user_peer = await self.resolve_peer(user_id) if user_id else None

        return await self.invoke(
            raw.functions.payments.GetStarsGiftOptions(
                user_id=user_peer,
            )
        )
