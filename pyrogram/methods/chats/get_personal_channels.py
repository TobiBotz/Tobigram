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

from typing import List, Optional, Union

import pyrogram
from pyrogram import raw, types


class GetPersonalChannels:
    async def get_personal_channels(
        self: "pyrogram.Client",
        for_community_peer: Union[int, str] = None
    ) -> Optional[List["types.Chat"]]:
        """Get all your public channels.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            for_community_peer (``int`` | ``str``, *optional*):
                Unique identifier (int) or username (str) of the community to get channels for.

        Returns:
            List of :obj:`~pyrogram.types.Chat`: On success, a list of personal channels is returned.

        Example:
            .. code-block:: python

                # Get all your personal channels
                await app.get_personal_channels()
        """
        r = await self.invoke(
            raw.functions.channels.GetAdminedPublicChannels(
                for_personal=True,
                for_community_peer=await self.resolve_peer(for_community_peer) if for_community_peer is not None else None
            )
        )

        return types.List(types.Chat._parse_chat(self, i) for i in r.chats) or None

