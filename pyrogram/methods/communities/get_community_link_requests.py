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


class GetCommunityLinkRequests:
    async def get_community_link_requests(
        self: pyrogram.Client,
        community_id: int | str,
        offset: str = "",
        limit: int = 100,
    ) -> raw.types.communities.PeerLinkRequests:
        """Get pending chat link requests for a community.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            community_id (``int`` | ``str``):
                Target community identifier.

            offset (``str``, *optional*):
                Offset for pagination. Defaults to "".

            limit (``int``, *optional*):
                Maximum number of requests to return. Defaults to 100.

        Returns:
            :obj:`~pyrogram.raw.types.communities.PeerLinkRequests`: Link requests object.

        Example:
            .. code-block:: python

                requests = await app.get_community_link_requests(community_id)
        """
        comm_peer = await self.resolve_peer(community_id)

        return await self.invoke(
            raw.functions.communities.GetPeerLinkRequests(
                community=utils.get_input_channel(comm_peer),
                offset=offset,
                limit=limit,
            )
        )
