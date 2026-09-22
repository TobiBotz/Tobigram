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


class UpdateConnectedBot:
    async def update_connected_bot(
        self: pyrogram.Client,
        bot: int | str | raw.base.InputUser,
        recipients: raw.base.InputBusinessBotRecipients,
        deleted: bool | None = None,
        rights: raw.base.BusinessBotRights | None = None,
    ) -> raw.base.Updates:
        """Connect a business bot to the current account, or change connection settings.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            bot (``int`` | ``str`` | :obj:`~pyrogram.raw.base.InputUser`):
                The bot to connect or disconnect.

            recipients (:obj:`~pyrogram.raw.base.InputBusinessBotRecipients`):
                Configuration for the business connection.

            deleted (``bool``, *optional*):
                Whether to fully disconnect the bot.

            rights (:obj:`~pyrogram.raw.base.BusinessBotRights`, *optional*):
                Business bot rights.

        Returns:
            :obj:`~pyrogram.raw.base.Updates`: On success, updates are returned.
        """
        input_bot = bot if isinstance(bot, raw.base.InputUser) else await self.resolve_peer(bot)

        return await self.invoke(
            raw.functions.account.UpdateConnectedBot(
                bot=input_bot,
                recipients=recipients,
                deleted=deleted,
                rights=rights,
            )
        )
