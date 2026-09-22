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


class InitPasskeyLogin:
    async def init_passkey_login(
        self: pyrogram.Client,
        api_id: int | None = None,
        api_hash: str | None = None,
    ) -> raw.base.auth.PasskeyLoginOptions:
        """Initialize login with a passkey over an unauthenticated connection.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            api_id (``int``, *optional*):
                Application identifier. Defaults to the client's api_id.

            api_hash (``str``, *optional*):
                Application identifier hash. Defaults to the client's api_hash.

        Returns:
            :obj:`~pyrogram.raw.base.auth.PasskeyLoginOptions`: The passkey login options.

        Example:
            .. code-block:: python

                options = await app.init_passkey_login()
        """
        return await self.invoke(
            raw.functions.auth.InitPasskeyLogin(
                api_id=api_id or self.api_id,
                api_hash=api_hash or self.api_hash,
            )
        )
