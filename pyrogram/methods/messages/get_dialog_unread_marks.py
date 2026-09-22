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


class GetDialogUnreadMarks:
    async def get_dialog_unread_marks(
        self: pyrogram.Client,
        parent_peer: int | str | None = None,
    ) -> list[raw.base.DialogPeer]:
        """Get dialogs marked as unread.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            parent_peer (``int`` | ``str``, *optional*):
                Filter by parent peer (e.g., for saved messages).

        Returns:
            List of :obj:`~pyrogram.raw.base.DialogPeer`: The unread-marked dialogs.

        Example:
            .. code-block:: python

                dialogs = await app.get_dialog_unread_marks()
        """
        parent = await self.resolve_peer(parent_peer) if parent_peer else None

        return await self.invoke(raw.functions.messages.GetDialogUnreadMarks(parent_peer=parent))
