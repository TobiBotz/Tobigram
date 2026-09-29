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


class SaveDefaultGroupCallJoinAs:
    async def save_default_group_call_join_as(
        self: pyrogram.Client,
        chat_id: int | str,
        join_as: int | str,
    ) -> bool:
        """Save default peer identity (personal profile or channel) to join voice chats in a chat.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            join_as (``int`` | ``str``):
                Peer to join as (user profile or managed channel).

        Returns:
            ``bool``: On success, True is returned.
        """
        peer = await self.resolve_peer(chat_id)
        join_as_peer = await self.resolve_peer(join_as)

        return await self.invoke(
            raw.functions.phone.SaveDefaultGroupCallJoinAs(
                peer=peer,
                join_as=join_as_peer,
            )
        )
