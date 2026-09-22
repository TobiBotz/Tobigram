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


class SendEncrypted:
    async def send_encrypted(
        self: pyrogram.Client,
        peer: raw.base.InputEncryptedChat,
        random_id: int,
        data: bytes,
        silent: bool | None = None,
    ) -> raw.base.messages.SentEncryptedMessage:
        """Send an encrypted message to a secret chat.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            peer (:obj:`~pyrogram.raw.base.InputEncryptedChat`):
                The secret chat to send to.

            random_id (``int``):
                Random ID for deduplication.

            data (``bytes``):
                The encrypted message bytes.

            silent (``bool``, *optional*):
                If True, send without notification.

        Returns:
            :obj:`~pyrogram.raw.base.messages.SentEncryptedMessage`: The sent message info.

        Example:
            .. code-block:: python

                await app.send_encrypted(peer, random_id=123, data=b"...")
        """
        return await self.invoke(
            raw.functions.messages.SendEncrypted(
                peer=peer,
                random_id=random_id,
                data=data,
                silent=silent,
            )
        )
