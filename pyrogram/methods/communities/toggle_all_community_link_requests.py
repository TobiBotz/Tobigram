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


class ToggleAllCommunityLinkRequests:
    async def toggle_all_community_link_requests(
        self: pyrogram.Client,
        community_id: int | str,
        reject: bool | None = None,
    ) -> bool:
        """Approve or reject all pending chat link requests for a community in bulk.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            community_id (``int`` | ``str``):
                Target community identifier.

            reject (``bool``, *optional*):
                Pass True to reject all, or False/None to approve all.

        Returns:
            ``bool``: True on success.

        Example:
            .. code-block:: python

                # Approve all
                await app.toggle_all_community_link_requests(community_id)

                # Reject all
                await app.toggle_all_community_link_requests(community_id, reject=True)
        """
        comm_peer = await self.resolve_peer(community_id)

        return await self.invoke(
            raw.functions.communities.ToggleAllPeerLinkRequestApproval(
                community=comm_peer,
                reject=reject,
            )
        )
