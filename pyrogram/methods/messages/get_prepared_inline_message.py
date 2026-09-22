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


class GetPreparedInlineMessage:
    async def get_prepared_inline_message(
        self: pyrogram.Client,
        bot_id: int | str,
        message_id: str,
    ) -> raw.base.messages.PreparedInlineMessage:
        """Get a prepared inline message by ID.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            bot_id (``int`` | ``str``):
                The bot that created the prepared message.

            message_id (``str``):
                The ID of the prepared inline message.

        Returns:
            :obj:`~pyrogram.raw.base.messages.PreparedInlineMessage`: The prepared inline message.

        Example:
            .. code-block:: python

                msg = await app.get_prepared_inline_message(bot, "msg_id")
        """
        bot = await self.resolve_peer(bot_id)

        return await self.invoke(
            raw.functions.messages.GetPreparedInlineMessage(bot=bot, id=message_id)
        )
