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

import logging

import pyrogram
from pyrogram import raw, types, utils
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable

log = logging.getLogger(__name__)


class GetScheduledMessages:
    async def get_scheduled_messages(
        self: pyrogram.Client,
        chat_id: int | str,
        message_ids: int | Iterable[int] | None = None,
    ) -> list[types.Message] | types.Message:
        """Get one or more scheduled messages from a chat.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).

            message_ids (``int`` | Iterable of ``int``, *optional*):
                Pass a single message identifier or an iterable of message ids (as integers) to get specific scheduled messages.
                If not passed, all scheduled messages are returned.

        Returns:
            :obj:`~pyrogram.types.Message` | List of :obj:`~pyrogram.types.Message`: In case *message_ids* was
            a single integer, a single message is returned (or None if not found). Otherwise, a list of messages is returned.

        Example:
            .. code-block:: python

                # Get all scheduled messages
                await app.get_scheduled_messages(chat_id)

                # Get specific scheduled message
                await app.get_scheduled_messages(chat_id, 12345)

                # Get multiple specific scheduled messages
                await app.get_scheduled_messages(chat_id, [12345, 12346])

        Raises:
            ValueError: In case of invalid arguments.
        """
        peer = await self.resolve_peer(chat_id)

        if message_ids is not None:
            is_iterable = not isinstance(message_ids, int)
            ids = list(message_ids) if is_iterable else [message_ids]
            r = await self.invoke(raw.functions.messages.GetScheduledMessages(peer=peer, id=ids))
            messages = await utils.parse_messages(self, r, replies=0, is_scheduled=True)
            return messages if is_iterable else messages[0] if messages else None

        r = await self.invoke(raw.functions.messages.GetScheduledHistory(peer=peer, hash=0))

        return await utils.parse_messages(self, r, replies=0, is_scheduled=True)
