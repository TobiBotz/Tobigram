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


class GetChatlistUpdates:
    async def get_chatlist_updates(
        self: pyrogram.Client,
        chatlist: int | raw.base.InputChatlist,
    ) -> raw.base.chatlists.ChatlistUpdates:
        """Fetch new chats associated with an imported chat folder deep link.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chatlist (``int`` | :obj:`~pyrogram.raw.base.InputChatlist`):
                The chat folder ID or InputChatlist object.

        Returns:
            :obj:`~pyrogram.raw.base.chatlists.ChatlistUpdates`: The chatlist updates object.

        Example:
            .. code-block:: python

                updates = await app.get_chatlist_updates(folder_id)
        """
        if isinstance(chatlist, int):
            chatlist = raw.types.InputChatlistDialogFilter(filter_id=chatlist)

        return await self.invoke(
            raw.functions.chatlists.GetChatlistUpdates(
                chatlist=chatlist,
            )
        )
