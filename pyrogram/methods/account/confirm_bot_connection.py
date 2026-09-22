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


class ConfirmBotConnection:
    async def confirm_bot_connection(
        self: pyrogram.Client,
        bot_id: int | str | raw.base.InputUser,
    ) -> bool:
        """Confirm a bot connection.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            bot_id (``int`` | ``str`` | :obj:`~pyrogram.raw.base.InputUser`):
                Bot to confirm connection for.

        Returns:
            ``bool``: On success, True is returned.
        """
        input_user = (
            bot_id if isinstance(bot_id, raw.base.InputUser) else await self.resolve_peer(bot_id)
        )

        return await self.invoke(
            raw.functions.account.ConfirmBotConnection(
                bot_id=input_user,
            )
        )
