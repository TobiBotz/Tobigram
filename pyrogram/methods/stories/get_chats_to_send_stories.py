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


class GetChatsToSendStories:
    async def get_chats_to_send_stories(
        self: pyrogram.Client,
    ) -> list[types.Chat]:
        """Get a list of chats and channels where the current user can post stories.

        .. include:: /_includes/usable-by/users.rst

        Returns:
            List of :obj:`~pyrogram.types.Chat`: On success, a list of chats is returned.

        Example:
            .. code-block:: python

                chats = await app.get_chats_to_send_stories()
        """
        r = await self.invoke(raw.functions.stories.GetChatsToSend())

        return [types.Chat._parse_chat(self, chat) for chat in r.chats]
