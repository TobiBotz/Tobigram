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


class SendEncryptedFile:
    async def send_encrypted_file(
        self: pyrogram.Client,
        peer: raw.base.InputEncryptedChat,
        random_id: int,
        data: bytes,
        file: raw.base.InputEncryptedFile,
        silent: bool | None = None,
    ) -> raw.base.messages.SentEncryptedMessage:
        """Send an encrypted file to a secret chat.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            peer (:obj:`~pyrogram.raw.base.InputEncryptedChat`):
                The secret chat to send to.

            random_id (``int``):
                Random ID for deduplication.

            data (``bytes``):
                The encrypted message bytes.

            file (:obj:`~pyrogram.raw.base.InputEncryptedFile`):
                The encrypted file to attach.

            silent (``bool``, *optional*):
                If True, send without notification.

        Returns:
            :obj:`~pyrogram.raw.base.messages.SentEncryptedMessage`: The sent message info.

        Example:
            .. code-block:: python

                await app.send_encrypted_file(peer, random_id=123, data=b"...", file=enc_file)
        """
        return await self.invoke(
            raw.functions.messages.SendEncryptedFile(
                peer=peer,
                random_id=random_id,
                data=data,
                file=file,
                silent=silent,
            )
        )
