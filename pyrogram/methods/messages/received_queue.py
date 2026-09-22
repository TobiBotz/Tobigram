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


class ReceivedQueue:
    async def received_queue(
        self: pyrogram.Client,
        max_qts: int,
    ) -> list[int]:
        """Acknowledge received secret chat messages up to a given QTS.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            max_qts (``int``):
                The maximum QTS (query timestamp) to acknowledge.

        Returns:
            List of ``int``: Acknowledged message IDs.

        Example:
            .. code-block:: python

                await app.received_queue(max_qts=50)
        """
        return await self.invoke(raw.functions.messages.ReceivedQueue(max_qts=max_qts))
