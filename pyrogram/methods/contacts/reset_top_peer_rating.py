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


class ResetTopPeerRating:
    async def reset_top_peer_rating(
        self: pyrogram.Client,
        category: raw.base.TopPeerCategory,
        peer: int | str | raw.base.InputPeer,
    ) -> bool:
        """Reset rating of a top peer in a given category.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            category (:obj:`~pyrogram.raw.base.TopPeerCategory`):
                Top peer category.

            peer (``int`` | ``str`` | :obj:`~pyrogram.raw.base.InputPeer`):
                Target peer whose rating should be reset.

        Returns:
            ``bool``: On success, True is returned.

        Example:
            .. code-block:: python

                from pyrogram import raw

                await app.reset_top_peer_rating(
                    category=raw.types.TopPeerCategoryCorrespondents(),
                    peer="username"
                )
        """
        return await self.invoke(
            raw.functions.contacts.ResetTopPeerRating(
                category=category,
                peer=peer
                if isinstance(peer, raw.base.InputPeer)
                else await self.resolve_peer(peer),
            )
        )
