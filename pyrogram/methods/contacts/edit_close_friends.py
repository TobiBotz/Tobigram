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


class EditCloseFriends:
    async def edit_close_friends(
        self: pyrogram.Client,
        user_ids: list[int | str],
    ) -> bool:
        """Edit the close friends list.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            user_ids (List of ``int`` | ``str``):
                Full list of user IDs or usernames of close friends.

        Returns:
            ``bool``: On success, True is returned.

        Example:
            .. code-block:: python

                await app.edit_close_friends([123456, 789012])
        """
        resolved_ids = []
        for u in user_ids:
            if isinstance(u, int):
                resolved_ids.append(u)
            else:
                peer = await self.resolve_peer(u)
                resolved_ids.append(peer.user_id)

        return await self.invoke(
            raw.functions.contacts.EditCloseFriends(
                id=resolved_ids,
            )
        )
