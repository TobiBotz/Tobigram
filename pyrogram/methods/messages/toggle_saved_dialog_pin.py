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


class ToggleSavedDialogPin:
    async def toggle_saved_dialog_pin(
        self: pyrogram.Client,
        peer: int | str,
        pinned: bool = True,
    ) -> bool:
        """Pin or unpin a dialog in Saved Messages.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            peer (``int`` | ``str``):
                Unique identifier (int) or username (str) of the peer to pin.

            pinned (``bool``, *optional*):
                Pass True to pin, False to unpin. Defaults to True.

        Returns:
            ``bool``: True on success.

        Example:
            .. code-block:: python

                await app.toggle_saved_dialog_pin(user_id, pinned=True)
        """
        resolved = await self.resolve_peer(peer)

        return await self.invoke(
            raw.functions.messages.ToggleSavedDialogPin(
                peer=raw.types.InputDialogPeer(peer=resolved),
                pinned=pinned,
            )
        )
