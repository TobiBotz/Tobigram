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


class SetChatAvailableReactions:
    async def set_chat_available_reactions(
        self: pyrogram.Client,
        chat_id: int | str,
        available_reactions: raw.base.ChatReactions,
        reactions_limit: int | None = None,
        paid_enabled: bool | None = None,
    ) -> raw.base.Updates:
        """Set allowed reactions in a chat or channel.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Target chat identifier.

            available_reactions (:obj:`~pyrogram.raw.base.ChatReactions`):
                Allowed reactions.

            reactions_limit (``int``, *optional*):
                Maximum number of reactions per message.

            paid_enabled (``bool``, *optional*):
                Whether paid reactions are enabled.

        Returns:
            :obj:`~pyrogram.raw.base.Updates`: Updates.
        """
        peer = await self.resolve_peer(chat_id)
        return await self.invoke(
            raw.functions.messages.SetChatAvailableReactions(
                peer=peer,
                available_reactions=available_reactions,
                reactions_limit=reactions_limit,
                paid_enabled=paid_enabled,
            )
        )
