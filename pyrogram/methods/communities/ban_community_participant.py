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


class BanCommunityParticipant:
    async def ban_community_participant(
        self: pyrogram.Client,
        community_id: int | str,
        user_id: int | str,
        unban: bool = False,
    ) -> bool:
        """Ban or unban a participant from an entire community.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            community_id (``int`` | ``str``):
                Target community identifier.

            user_id (``int`` | ``str``):
                Target user ID or username to ban/unban.

            unban (``bool``, *optional*):
                Pass True to unban, False to ban. Defaults to False.

        Returns:
            ``bool``: True on success.

        Example:
            .. code-block:: python

                # Ban user
                await app.ban_community_participant(community_id, user_id)

                # Unban user
                await app.ban_community_participant(community_id, user_id, unban=True)
        """
        comm_peer = await self.resolve_peer(community_id)
        user_peer = await self.resolve_peer(user_id)

        return await self.invoke(
            raw.functions.communities.ToggleParticipantBanned(
                community=comm_peer,
                participant=user_peer,
                unban=unban,
            )
        )
