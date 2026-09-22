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


class ImportWebTokenAuthorization:
    async def import_web_token_authorization(
        self: pyrogram.Client,
        web_auth_token: str,
        api_id: int | None = None,
        api_hash: str | None = None,
    ) -> raw.base.auth.Authorization:
        """Login by importing a web authorization token.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            web_auth_token (``str``):
                The web authorization token.

            api_id (``int``, *optional*):
                Application identifier. Defaults to the client's api_id.

            api_hash (``str``, *optional*):
                Application identifier hash. Defaults to the client's api_hash.

        Returns:
            :obj:`~pyrogram.raw.base.auth.Authorization`: The authorization object.

        Example:
            .. code-block:: python

                auth = await app.import_web_token_authorization(token)
        """
        return await self.invoke(
            raw.functions.auth.ImportWebTokenAuthorization(
                api_id=api_id or self.api_id,
                api_hash=api_hash or self.api_hash,
                web_auth_token=web_auth_token,
            )
        )
