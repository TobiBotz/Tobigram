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

from typing import Union

import pyrogram
from pyrogram import raw


class DeleteParticipantReactions:
    async def delete_participant_reactions(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        participant_id: Union[int, str],
    ) -> bool:
        """Remove all reactions of a specific participant from every message in a group or channel.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            participant_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the participant whose reactions will be removed.

        Returns:
            ``bool``: True on success.

        Example:
            .. code-block:: python

                # Remove all reactions by a user in a chat
                await app.delete_participant_reactions(chat_id, participant_id)
        """
        return await self.invoke(
            raw.functions.messages.DeleteParticipantReactions(
                peer=await self.resolve_peer(chat_id),
                participant=await self.resolve_peer(participant_id)
            )
        )
