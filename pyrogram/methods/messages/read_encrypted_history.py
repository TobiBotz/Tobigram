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


class ReadEncryptedHistory:
    async def read_encrypted_history(
        self: pyrogram.Client,
        peer: raw.base.InputEncryptedChat,
        max_date: int,
    ) -> bool:
        """Mark the history of a secret chat as read up to a given date.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            peer (:obj:`~pyrogram.raw.base.InputEncryptedChat`):
                The secret chat.

            max_date (``int``):
                The maximum message date to mark as read.

        Returns:
            ``bool``: True on success.

        Example:
            .. code-block:: python

                await app.read_encrypted_history(peer, max_date=1700000000)
        """
        return await self.invoke(
            raw.functions.messages.ReadEncryptedHistory(peer=peer, max_date=max_date)
        )
