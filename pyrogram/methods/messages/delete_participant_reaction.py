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
from pyrogram import raw, types, utils


class DeleteParticipantReaction:
    async def delete_participant_reaction(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        message_id: int,
        participant_id: Union[int, str],
    ) -> Union["types.Message", bool]:
        """Remove all reactions of a specific participant from a single message.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            message_id (``int``):
                Identifier of the message.

            participant_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the participant whose reactions will be removed.

        Returns:
            :obj:`~pyrogram.types.Message` | ``bool``: On success, the updated message is returned (when available),
            otherwise True is returned.

        Example:
            .. code-block:: python

                # Remove all reactions by a user from a specific message
                await app.delete_participant_reaction(chat_id, message_id, participant_id)
        """
        r = await self.invoke(
            raw.functions.messages.DeleteParticipantReaction(
                peer=await self.resolve_peer(chat_id),
                msg_id=message_id,
                participant=await self.resolve_peer(participant_id)
            )
        )

        return next(iter(await utils.parse_messages(client=self, messages=r)), True)
