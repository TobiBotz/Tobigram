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


class RequestEncryption:
    async def request_encryption(
        self: pyrogram.Client,
        user_id: int | str,
        random_id: int,
        g_a: bytes,
    ) -> raw.base.EncryptedChat:
        """Request an end-to-end encrypted chat (secret chat) with a user.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            user_id (``int`` | ``str``):
                The user to open a secret chat with.

            random_id (``int``):
                Random ID for the request.

            g_a (``bytes``):
                The Diffie-Hellman public key.

        Returns:
            :obj:`~pyrogram.raw.base.EncryptedChat`: The encrypted chat object.

        Example:
            .. code-block:: python

                chat = await app.request_encryption(user_id, random_id=123, g_a=b"...")
        """
        peer = await self.resolve_peer(user_id)

        return await self.invoke(
            raw.functions.messages.RequestEncryption(
                user_id=peer,
                random_id=random_id,
                g_a=g_a,
            )
        )
