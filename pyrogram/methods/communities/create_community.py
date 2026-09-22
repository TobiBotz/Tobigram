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


class CreateCommunity:
    async def create_community(
        self: pyrogram.Client,
        title: str,
        chat_id: int | str,
        about: str | None = None,
        hidden: bool | None = None,
    ) -> raw.types.Updates:
        """Create a new Telegram Community around a channel or supergroup.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            title (``str``):
                The title of the new community.

            chat_id (``int`` | ``str``):
                The root channel or supergroup identifier for the community.

            about (``str``, *optional*):
                Description of the community.

            hidden (``bool``, *optional*):
                Whether the community should be hidden.

        Returns:
            :obj:`~pyrogram.raw.types.Updates`: On success, updates are returned.

        Example:
            .. code-block:: python

                community = await app.create_community("Developers Hub", channel_id)
        """
        peer = await self.resolve_peer(chat_id)

        return await self.invoke(
            raw.functions.communities.Create(
                title=title,
                peer=peer,
                about=about,
                hidden=hidden,
            )
        )
