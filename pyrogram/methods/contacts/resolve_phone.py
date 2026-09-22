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


class ResolvePhone:
    async def resolve_phone(
        self: pyrogram.Client,
        phone: str,
    ) -> raw.base.contacts.ResolvedPeer:
        """Resolve a phone number to get user info, if their privacy settings allow it.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            phone (``str``):
                Phone number in international format.

        Returns:
            :obj:`~pyrogram.raw.base.contacts.ResolvedPeer`: Resolved peer object.

        Example:
            .. code-block:: python

                peers = await app.resolve_phone("+1234567890")
        """
        return await self.invoke(
            raw.functions.contacts.ResolvePhone(
                phone=phone,
            )
        )
