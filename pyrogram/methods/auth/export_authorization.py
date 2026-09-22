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


class ExportAuthorization:
    async def export_authorization(
        self: pyrogram.Client,
        dc_id: int,
    ) -> raw.base.auth.ExportedAuthorization:
        """Export session authorization data to copy to another data center.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            dc_id (``int``):
                Number of the target data center.

        Returns:
            :obj:`~pyrogram.raw.base.auth.ExportedAuthorization`: The exported authorization.

        Example:
            .. code-block:: python

                exported = await app.export_authorization(2)
        """
        return await self.invoke(
            raw.functions.auth.ExportAuthorization(
                dc_id=dc_id,
            )
        )
