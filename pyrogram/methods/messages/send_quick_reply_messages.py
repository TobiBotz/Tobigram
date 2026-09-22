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


class SendQuickReplyMessages:
    async def send_quick_reply_messages(
        self: pyrogram.Client,
        chat_id: int | str,
        shortcut_id: int,
        message_ids: list[int] | int,
    ) -> raw.base.Updates:
        """Send messages from a quick reply shortcut into a target chat.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Target chat identifier.

            shortcut_id (``int``):
                The quick reply shortcut ID.

            message_ids (``list[int]`` | ``int``):
                Message IDs from the shortcut to send.

        Returns:
            :obj:`~pyrogram.raw.base.Updates`: Updates.
        """
        ids = [message_ids] if isinstance(message_ids, int) else message_ids
        random_ids = [self.rnd_id() for _ in ids]
        peer = await self.resolve_peer(chat_id)
        return await self.invoke(
            raw.functions.messages.SendQuickReplyMessages(
                peer=peer,
                shortcut_id=shortcut_id,
                id=ids,
                random_id=random_ids,
            )
        )
