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
from pyrogram import raw, types


class GetInactiveChannels:
    async def get_inactive_channels(
        self: pyrogram.Client,
    ) -> list[types.Chat]:
        """Get the list of inactive channels and supergroups.

        Telegram returns inactive channels you are a member of, which can be left
        when reaching channel join limits.

        .. include:: /_includes/usable-by/users.rst

        Returns:
            List of :obj:`~pyrogram.types.Chat`: On success, a list of inactive chats is returned.

        Example:
            .. code-block:: python

                # Get inactive channels
                inactive = await app.get_inactive_channels()
                for chat in inactive:
                    print(chat.title)
        """
        r = await self.invoke(raw.functions.channels.GetInactiveChannels())

        return types.List([types.Chat._parse_chat(self, chat) for chat in r.chats])
