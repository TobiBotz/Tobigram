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


class RequestWebViewButton:
    async def request_web_view_button(
        self: pyrogram.Client,
        user_id: int | str,
        button: raw.base.KeyboardButton,
    ) -> raw.base.bots.RequestedButton:
        """Prepare a peer request button for a Mini App (for bots).

        .. include:: /_includes/usable-by/bots.rst

        Parameters:
            user_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target user.

            button (:obj:`~pyrogram.raw.base.KeyboardButton`):
                The button to prepare.

        Returns:
            :obj:`~pyrogram.raw.base.bots.RequestedButton`: The requested button information.

        Example:
            .. code-block:: python

                res = await bot.request_web_view_button(12345, button)
        """
        return await self.invoke(
            raw.functions.bots.RequestWebViewButton(
                user_id=await self.resolve_peer(user_id),
                button=button,
            )
        )
