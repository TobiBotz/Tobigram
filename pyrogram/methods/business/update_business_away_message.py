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
# Source: tl:account.updateBusinessAwayMessage
# ***************************

from typing import Union, Optional

import pyrogram
from pyrogram import raw
from pyrogram import types


class UpdateBusinessAwayMessage:
    async def update_business_away_message(
        self: "pyrogram.Client",
        message: raw.types.InputBusinessAwayMessage = None,
    ) -> "types.Message":
        """Set an automatic away message when you are offline.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            message (raw.types.InputBusinessAwayMessage): Away message config (shortcut_id + schedule + recipients)

        Returns:
            :obj:`~pyrogram.types.Message`

        Example:
            .. code-block:: python

                await app.update_business_away_message(...)
        """

        r = await self.invoke(
            raw.functions.account.updateBusinessAwayMessage(
                message=message,
            )
        )
