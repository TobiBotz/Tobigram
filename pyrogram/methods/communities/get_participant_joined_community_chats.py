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


class GetParticipantJoinedCommunityChats:
    async def get_participant_joined_community_chats(
        self: pyrogram.Client,
        community_id: int | str,
        user_id: int | str = "me",
    ) -> raw.types.communities.ParticipantJoinedChats:
        """Get the list of chats within a community that a specific participant has joined.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            community_id (``int`` | ``str``):
                Target community identifier.

            user_id (``int`` | ``str``, *optional*):
                Target user ID or "me". Defaults to "me".

        Returns:
            :obj:`~pyrogram.raw.types.communities.ParticipantJoinedChats`: Participant joined chats object.

        Example:
            .. code-block:: python

                chats = await app.get_participant_joined_community_chats(community_id, "me")
        """
        comm_peer = await self.resolve_peer(community_id)
        user_peer = await self.resolve_peer(user_id)

        return await self.invoke(
            raw.functions.communities.GetParticipantJoinedChats(
                community=comm_peer,
                participant=user_peer,
            )
        )
