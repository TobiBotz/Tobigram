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


class GetSavedReactionTags:
    async def get_saved_reaction_tags(
        self: pyrogram.Client,
        peer_id: int | str | None = None,
        hash: int = 0,
    ) -> raw.base.messages.SavedReactionTags:
        """Get reaction tags assigned to saved messages.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            peer_id (``int`` | ``str``, *optional*):
                Target dialog peer. Defaults to None.

            hash (``int``, *optional*):
                Hash for caching. Defaults to 0.

        Returns:
            :obj:`~pyrogram.raw.base.messages.SavedReactionTags`: Saved reaction tags.
        """
        peer = await self.resolve_peer(peer_id) if peer_id is not None else None
        return await self.invoke(
            raw.functions.messages.GetSavedReactionTags(
                peer=peer,
                hash=hash,
            )
        )
