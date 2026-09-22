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


class ExportContactToken:
    async def export_contact_token(
        self: pyrogram.Client,
    ) -> raw.base.ExportedContactToken:
        """Generate a temporary profile link token for the currently logged-in user.

        .. include:: /_includes/usable-by/users.rst

        Returns:
            :obj:`~pyrogram.raw.base.ExportedContactToken`: The exported contact token.

        Example:
            .. code-block:: python

                token = await app.export_contact_token()
        """
        return await self.invoke(raw.functions.contacts.ExportContactToken())
