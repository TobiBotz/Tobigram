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


class ChangeAuthorizationSettings:
    async def change_authorization_settings(
        self: pyrogram.Client,
        hash: int,
        confirmed: bool | None = None,
        encrypted_requests_disabled: bool | None = None,
        call_requests_disabled: bool | None = None,
    ) -> bool:
        """Change settings related to a session.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            hash (``int``):
                Session ID from the authorization constructor.

            confirmed (``bool``, *optional*):
                If set, confirms a newly logged in session.

            encrypted_requests_disabled (``bool``, *optional*):
                Whether to disable receiving encrypted chats.

            call_requests_disabled (``bool``, *optional*):
                Whether to disable receiving calls.

        Returns:
            ``bool``: On success, True is returned.
        """
        return await self.invoke(
            raw.functions.account.ChangeAuthorizationSettings(
                hash=hash,
                confirmed=confirmed,
                encrypted_requests_disabled=encrypted_requests_disabled,
                call_requests_disabled=call_requests_disabled,
            )
        )
