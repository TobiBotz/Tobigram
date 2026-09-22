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


class AcceptLoginToken:
    async def accept_login_token(
        self: pyrogram.Client,
        token: bytes,
    ) -> raw.base.Authorization:
        """Accept a QR code login token, logging in the app that generated it.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            token (``bytes``):
                Login token embedded in QR code.

        Returns:
            :obj:`~pyrogram.raw.base.Authorization`: The authorization object.

        Example:
            .. code-block:: python

                auth = await app.accept_login_token(token)
        """
        return await self.invoke(
            raw.functions.auth.AcceptLoginToken(
                token=token,
            )
        )
