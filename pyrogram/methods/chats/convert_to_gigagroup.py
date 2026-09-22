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


class ConvertToGigagroup:
    async def convert_to_gigagroup(
        self: pyrogram.Client,
        chat_id: int | str,
    ) -> bool:
        """Convert a supergroup to a gigagroup (broadcast group).

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target supergroup.

        Returns:
            ``bool``: True on success.

        Example:
            .. code-block:: python

                await app.convert_to_gigagroup(chat_id)
        """
        peer = await self.resolve_peer(chat_id)

        await self.invoke(
            raw.functions.channels.ConvertToGigagroup(
                channel=peer,
            )
        )

        return True
