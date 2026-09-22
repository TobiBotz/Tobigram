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


class GetFactCheck:
    async def get_fact_check(
        self: pyrogram.Client,
        chat_id: int | str,
        message_ids: list[int],
    ) -> list[raw.base.FactCheck]:
        """Get fact-check information for one or more messages.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            message_ids (List of ``int``):
                The IDs of the messages to check.

        Returns:
            List of :obj:`~pyrogram.raw.base.FactCheck`: The fact checks.

        Example:
            .. code-block:: python

                checks = await app.get_fact_check(chat_id, [123])
        """
        peer = await self.resolve_peer(chat_id)

        return await self.invoke(raw.functions.messages.GetFactCheck(peer=peer, msg_id=message_ids))
