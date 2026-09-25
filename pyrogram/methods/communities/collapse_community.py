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
from pyrogram import raw, utils


class CollapseCommunity:
    async def collapse_community(
        self: pyrogram.Client,
        community_id: int | str,
        collapsed: bool = True,
    ) -> raw.types.Updates:
        """Collapse or expand a community folder in the user's dialogs list.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            community_id (``int`` | ``str``):
                Target community identifier.

            collapsed (``bool``, *optional*):
                Pass True to collapse, False to expand. Defaults to True.

        Returns:
            :obj:`~pyrogram.raw.types.Updates`: On success, updates are returned.

        Example:
            .. code-block:: python

                await app.collapse_community(community_id, True)
        """
        comm_peer = await self.resolve_peer(community_id)

        return await self.invoke(
            raw.functions.communities.ToggleCommunityCollapsedInDialogs(
                community=utils.get_input_channel(comm_peer),
                collapsed=collapsed,
            )
        )
