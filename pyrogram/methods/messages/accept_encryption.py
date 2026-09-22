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


class AcceptEncryption:
    async def accept_encryption(
        self: pyrogram.Client,
        peer: raw.base.InputEncryptedChat,
        g_b: bytes,
        key_fingerprint: int,
    ) -> raw.base.EncryptedChat:
        """Accept an incoming end-to-end encrypted chat request.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            peer (:obj:`~pyrogram.raw.base.InputEncryptedChat`):
                The encrypted chat to accept.

            g_b (``bytes``):
                The Diffie-Hellman public key from the other party.

            key_fingerprint (``int``):
                Fingerprint of the shared key.

        Returns:
            :obj:`~pyrogram.raw.base.EncryptedChat`: The accepted encrypted chat.

        Example:
            .. code-block:: python

                chat = await app.accept_encryption(peer, g_b=b"...", key_fingerprint=123)
        """
        return await self.invoke(
            raw.functions.messages.AcceptEncryption(
                peer=peer,
                g_b=g_b,
                key_fingerprint=key_fingerprint,
            )
        )
