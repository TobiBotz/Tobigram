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


class FinishFirebasePnvLogin:
    async def finish_firebase_pnv_login(
        self: pyrogram.Client,
        google_token: str,
    ) -> raw.base.auth.Authorization:
        """Finish Firebase phone number verification login.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            google_token (``str``):
                The Google safety token.

        Returns:
            :obj:`~pyrogram.raw.base.auth.Authorization`: The authorization object.

        Example:
            .. code-block:: python

                auth = await app.finish_firebase_pnv_login(google_token)
        """
        return await self.invoke(
            raw.functions.auth.FinishFirebasePnvLogin(
                google_token=google_token,
            )
        )
