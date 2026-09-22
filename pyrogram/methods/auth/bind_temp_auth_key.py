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


class BindTempAuthKey:
    async def bind_temp_auth_key(
        self: pyrogram.Client,
        perm_auth_key_id: int,
        nonce: int,
        expires_at: int,
        encrypted_message: bytes,
    ) -> bool:
        """Bind a temporary authorization key to a permanent authorization key.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            perm_auth_key_id (``int``):
                Permanent auth_key_id to bind to.

            nonce (``int``):
                Random long integer nonce.

            expires_at (``int``):
                Unix timestamp after which the temporary key expires.

            encrypted_message (``bytes``):
                Encrypted binding message payload.

        Returns:
            ``bool``: On success, True is returned.

        Example:
            .. code-block:: python

                await app.bind_temp_auth_key(perm_id, nonce, expires_at, enc_msg)
        """
        return await self.invoke(
            raw.functions.auth.BindTempAuthKey(
                perm_auth_key_id=perm_auth_key_id,
                nonce=nonce,
                expires_at=expires_at,
                encrypted_message=encrypted_message,
            )
        )
