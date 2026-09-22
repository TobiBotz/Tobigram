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


class CheckHistoryImportPeer:
    async def check_history_import_peer(
        self: pyrogram.Client,
        chat_id: int | str,
    ) -> raw.base.messages.CheckedHistoryImportPeer:
        """Check if a chat history can be imported into a specific chat.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                The chat to check import support for.

        Returns:
            :obj:`~pyrogram.raw.base.messages.CheckedHistoryImportPeer`: The import check result.

        Example:
            .. code-block:: python

                result = await app.check_history_import_peer(chat_id)
        """
        peer = await self.resolve_peer(chat_id)

        return await self.invoke(raw.functions.messages.CheckHistoryImportPeer(peer=peer))
