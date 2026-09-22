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


class ViewSponsoredMessage:
    async def view_sponsored_message(
        self: pyrogram.Client,
        random_id: bytes,
    ) -> bool:
        """Mark a sponsored message as viewed.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            random_id (``bytes``):
                The random ID of the sponsored message.

        Returns:
            ``bool``: True on success.

        Example:
            .. code-block:: python

                await app.view_sponsored_message(random_id)
        """
        return await self.invoke(raw.functions.messages.ViewSponsoredMessage(random_id=random_id))
