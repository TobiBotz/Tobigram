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


class FinishPasskeyLogin:
    async def finish_passkey_login(
        self: pyrogram.Client,
        credential: raw.base.InputPasskeyCredential,
        from_dc_id: int | None = None,
        from_auth_key_id: int | None = None,
    ) -> raw.base.auth.Authorization:
        """Complete login with a passkey over an unauthenticated connection.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            credential (:obj:`~pyrogram.raw.base.InputPasskeyCredential`):
                Passkey assertion credential result.

            from_dc_id (``int``, *optional*):
                DC ID used for the initial passkey request.

            from_auth_key_id (``int``, *optional*):
                Auth key ID for the connection to from_dc_id.

        Returns:
            :obj:`~pyrogram.raw.base.auth.Authorization`: The authorization object.

        Example:
            .. code-block:: python

                auth = await app.finish_passkey_login(credential)
        """
        return await self.invoke(
            raw.functions.auth.FinishPasskeyLogin(
                credential=credential,
                from_dc_id=from_dc_id,
                from_auth_key_id=from_auth_key_id,
            )
        )
