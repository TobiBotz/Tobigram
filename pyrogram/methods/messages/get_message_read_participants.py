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
from pyrogram import raw, types


class GetMessageReadParticipants:
    async def get_message_read_participants(
        self: pyrogram.Client,
        chat_id: int | str,
        message_id: int,
    ) -> list[types.ReadParticipantDate]:
        """Get the list of participants who read a specific message in a chat.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            message_id (``int``):
                Identifier of the message.

        Returns:
            List of :obj:`~pyrogram.types.ReadParticipantDate`: On success, a list of participants and read dates is returned.

        Example:
            .. code-block:: python

                # Get read participants of a message
                readers = await app.get_message_read_participants(chat_id, message_id)
                for reader in readers:
                    print(reader.user_id, reader.date)
        """
        r = await self.invoke(
            raw.functions.messages.GetMessageReadParticipants(
                peer=await self.resolve_peer(chat_id),
                msg_id=message_id,
            )
        )

        return types.List([types.ReadParticipantDate._parse(self, item) for item in r])
