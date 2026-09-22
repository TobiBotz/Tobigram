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


class HidePeerSettingsBar:
    async def hide_peer_settings_bar(
        self: pyrogram.Client,
        chat_id: int | str,
    ) -> bool:
        """Hide the peer settings bar (the "Add to contacts" / "Block" bar) for a user.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target user.

        Returns:
            ``bool``: True on success.

        Example:
            .. code-block:: python

                await app.hide_peer_settings_bar(user_id)
        """
        peer = await self.resolve_peer(chat_id)

        return await self.invoke(raw.functions.messages.HidePeerSettingsBar(peer=peer))
