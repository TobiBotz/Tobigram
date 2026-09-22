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


class ReadMessageContents:
    async def read_message_contents(
        self: pyrogram.Client,
        message_ids: list[int],
    ) -> raw.base.messages.AffectedMessages:
        """Mark the content of messages as read (e.g., mark voice notes as listened).

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            message_ids (List of ``int``):
                The IDs of the messages to mark as read.

        Returns:
            :obj:`~pyrogram.raw.base.messages.AffectedMessages`: The affected messages.

        Example:
            .. code-block:: python

                await app.read_message_contents([123, 456])
        """
        return await self.invoke(raw.functions.messages.ReadMessageContents(id=message_ids))
