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


class ReorderPinnedDialogs:
    async def reorder_pinned_dialogs(
        self: pyrogram.Client,
        order: list[raw.base.InputDialogPeer],
        force: bool | None = None,
        folder_id: int = 0,
    ) -> bool:
        """Reorder pinned dialogs.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            order (List of :obj:`~pyrogram.raw.base.InputDialogPeer`):
                The new order of pinned dialogs.

            force (``bool``, *optional*):
                If True, remove any dialogs not in the order list from pinned.

            folder_id (``int``, *optional*):
                Folder ID. Pass 0 for the main folder.

        Returns:
            ``bool``: True on success.

        Example:
            .. code-block:: python

                await app.reorder_pinned_dialogs(order=[...])
        """
        return await self.invoke(
            raw.functions.messages.ReorderPinnedDialogs(
                order=order,
                force=force,
                folder_id=folder_id,
            )
        )
