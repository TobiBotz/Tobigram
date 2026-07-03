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

# ***************************
# GENERATED FILE - DO NOT EDIT
# Source: tl:account.updateBusinessIntro
# ***************************

from typing import Union, Optional

import pyrogram
from pyrogram import raw
from pyrogram import types


class UpdateBusinessIntro:
    async def update_business_intro(
        self: "pyrogram.Client",
        intro: raw.types.InputBusinessIntro = None,
    ) -> "types.Message":
        """Update your business intro (title, description, sticker).

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            intro (raw.types.InputBusinessIntro): Business intro with title, description, and optional sticker

        Returns:
            :obj:`~pyrogram.types.Message`

        Example:
            .. code-block:: python

                await app.update_business_intro(...)
        """

        r = await self.invoke(
            raw.functions.account.updateBusinessIntro(
                intro=intro,
            )
        )
