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


class UnregisterDevice:
    async def unregister_device(
        self: pyrogram.Client,
        token_type: int,
        token: str,
        other_uids: list[int] | None = None,
    ) -> bool:
        """Deletes a device by its token, stops sending PUSH notifications to it.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            token_type (``int``):
                Device token type.

            token (``str``):
                Device token.

            other_uids (List of ``int``, *optional*):
                List of user identifiers of other users currently using the client.

        Returns:
            ``bool``: On success, True is returned.
        """
        return await self.invoke(
            raw.functions.account.UnregisterDevice(
                token_type=token_type,
                token=token,
                other_uids=other_uids or [],
            )
        )
