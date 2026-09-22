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


class UploadEncryptedFile:
    async def upload_encrypted_file(
        self: pyrogram.Client,
        peer: raw.base.InputEncryptedChat,
        file: raw.base.InputEncryptedFile,
    ) -> raw.base.EncryptedFile:
        """Upload an encrypted file to a secret chat.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            peer (:obj:`~pyrogram.raw.base.InputEncryptedChat`):
                The secret chat to upload the file for.

            file (:obj:`~pyrogram.raw.base.InputEncryptedFile`):
                The encrypted file to upload.

        Returns:
            :obj:`~pyrogram.raw.base.EncryptedFile`: The uploaded encrypted file.

        Example:
            .. code-block:: python

                enc_file = await app.upload_encrypted_file(peer, file=input_enc_file)
        """
        return await self.invoke(raw.functions.messages.UploadEncryptedFile(peer=peer, file=file))
