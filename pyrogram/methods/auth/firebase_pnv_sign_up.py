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


class FirebasePnvSignUp:
    async def firebase_pnv_sign_up(
        self: pyrogram.Client,
        first_name: str,
        last_name: str = "",
        no_joined_notifications: bool | None = None,
    ) -> raw.base.auth.Authorization:
        """Sign up a user verified via Firebase phone number verification.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            first_name (``str``):
                The first name of the new user.

            last_name (``str``, *optional*):
                The last name of the new user. Defaults to empty string.

            no_joined_notifications (``bool``, *optional*):
                Whether to disable joined notifications.

        Returns:
            :obj:`~pyrogram.raw.base.auth.Authorization`: The authorization object.

        Example:
            .. code-block:: python

                auth = await app.firebase_pnv_sign_up("Dan")
        """
        return await self.invoke(
            raw.functions.auth.FirebasePnvSignUp(
                first_name=first_name,
                last_name=last_name,
                no_joined_notifications=no_joined_notifications,
            )
        )
