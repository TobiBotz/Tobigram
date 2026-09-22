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


class GetPeerMaxStoryIDs:
    async def get_peer_max_story_ids(
        self: pyrogram.Client,
        chat_ids: int | str | list[int | str],
    ) -> list[raw.types.RecentStory]:
        """Get the maximum read story identifier for one or more peers.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_ids (``int`` | ``str`` | List of ``int`` | ``str``):
                A single chat identifier or list of chat identifiers.

        Returns:
            List of :obj:`~pyrogram.raw.types.RecentStory`: On success, a list of recent story states is returned.

        Example:
            .. code-block:: python

                max_ids = await app.get_peer_max_story_ids(["me", 123456])
        """
        peers_list = [chat_ids] if isinstance(chat_ids, (int, str)) else list(chat_ids)
        resolved_peers = [await self.resolve_peer(p) for p in peers_list]

        return await self.invoke(
            raw.functions.stories.GetPeerMaxIDs(
                id=resolved_peers,
            )
        )
