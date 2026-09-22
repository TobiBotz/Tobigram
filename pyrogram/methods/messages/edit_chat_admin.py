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


class EditChatAdmin:
    async def edit_chat_admin(
        self: pyrogram.Client,
        chat_id: int,
        user_id: int | str,
        is_admin: bool,
    ) -> bool:
        """Make or revoke admin status in a basic group.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int``):
                The basic group chat ID.

            user_id (``int`` | ``str``):
                The user to promote or demote.

            is_admin (``bool``):
                Pass True to make admin, False to revoke.

        Returns:
            ``bool``: True on success.

        Example:
            .. code-block:: python

                await app.edit_chat_admin(-100123456, user_id, is_admin=True)
        """
        peer_user = await self.resolve_peer(user_id)

        return await self.invoke(
            raw.functions.messages.EditChatAdmin(
                chat_id=chat_id,
                user_id=peer_user,
                is_admin=is_admin,
            )
        )
