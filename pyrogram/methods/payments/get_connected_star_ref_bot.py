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


class GetConnectedStarRefBot:
    async def get_connected_star_ref_bot(
        self: pyrogram.Client,
        chat_id: int | str,
        bot_id: int | str,
    ) -> raw.types.payments.ConnectedStarRefBots:
        """Get details about a specific connected Star affiliate bot.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Target channel ID.

            bot_id (``int`` | ``str``):
                Bot identifier or username.

        Returns:
            :obj:`~pyrogram.raw.types.payments.ConnectedStarRefBots`: Connected bot information.

        Example:
            .. code-block:: python

                res = await app.get_connected_star_ref_bot(channel_id, "@affiliate_bot")
        """
        peer = await self.resolve_peer(chat_id)
        bot_peer = await self.resolve_peer(bot_id)

        return await self.invoke(
            raw.functions.payments.GetConnectedStarRefBot(
                peer=peer,
                bot=bot_peer,
            )
        )
