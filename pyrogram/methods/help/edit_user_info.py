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
from pyrogram import raw, utils


class EditUserInfo:
    async def edit_user_info(
        self: pyrogram.Client,
        user_id: int | str,
        message: str,
        entities: list[raw.base.MessageEntity] | None = None,
    ) -> raw.base.help.UserInfo:
        """Edit internal user info (for TSF members).

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            user_id (``int`` | ``str``):
                User ID.

            message (``str``):
                Message text.

            entities (List of :obj:`~pyrogram.raw.base.MessageEntity`, *optional*):
                Message entities for styled text.

        Returns:
            :obj:`~pyrogram.raw.base.help.UserInfo`: The updated user info.

        Example:
            .. code-block:: python

                info = await app.edit_user_info(user_id, "Notes on user")
        """
        return await self.invoke(
            raw.functions.help.EditUserInfo(
                user_id=utils.get_input_user(await self.resolve_peer(user_id)),
                message=message,
                entities=entities or [],
            )
        )
