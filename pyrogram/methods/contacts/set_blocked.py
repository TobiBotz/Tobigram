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


class SetBlocked:
    async def set_blocked(
        self: pyrogram.Client,
        peers: list[int | str | raw.base.InputPeer],
        my_stories_from: bool | None = None,
        limit: int = 100,
    ) -> bool:
        """Replace the contents of an entire blocklist.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            peers (List of ``int`` | ``str`` | :obj:`~pyrogram.raw.base.InputPeer`):
                Full list of peers to set in the blocklist.

            my_stories_from (``bool``, *optional*):
                Whether to edit the story blocklist; if not set, edits the main blocklist.

            limit (``int``, *optional*):
                Maximum number of results to return. Defaults to 100.

        Returns:
            ``bool``: On success, True is returned.

        Example:
            .. code-block:: python

                await app.set_blocked([12345, "spammer_user"])
        """
        resolved_peers = [
            p if isinstance(p, raw.base.InputPeer) else await self.resolve_peer(p) for p in peers
        ]
        return await self.invoke(
            raw.functions.contacts.SetBlocked(
                id=resolved_peers,
                limit=limit,
                my_stories_from=my_stories_from,
            )
        )
