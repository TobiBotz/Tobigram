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

from collections.abc import Iterable

import pyrogram
from pyrogram import types


class CopyMessages:
    async def copy_messages(
        self: pyrogram.Client,
        chat_id: int | str,
        from_chat_id: int | str,
        message_ids: int | Iterable[int],
        message_thread_id: int | None = None,
        direct_messages_topic_id: int | None = None,
        disable_notification: bool | None = None,
        protect_content: bool | None = None,
        remove_caption: bool | None = None,
    ) -> list[types.Message]:
        """Copy messages of any kind in bulk without a forward link.

        If some messages can't be copied they are skipped.
        This method is analogous to :meth:`~Client.forward_messages` but the copied
        messages have no link to the original.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            from_chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the source chat.

            message_ids (``int`` | Iterable of ``int``):
                Message identifiers in the source chat. Pass a single int or a list of ints.

            message_thread_id (``int``, *optional*):
                Unique identifier for the target message thread (topic) of the forum.
                For supergroups only.

            direct_messages_topic_id (``int``, *optional*):
                Unique identifier of the direct messages topic to copy into.

            disable_notification (``bool``, *optional*):
                Sends the messages silently. Users will receive a notification with no sound.

            protect_content (``bool``, *optional*):
                Protects the contents of the sent messages from forwarding and saving.

            remove_caption (``bool``, *optional*):
                Pass True to copy messages without their captions.

        Returns:
            List of :obj:`~pyrogram.types.Message`: A list of the copied messages.

        Example:
            .. code-block:: python

                # Copy a single message
                await app.copy_messages(to_chat, from_chat, 123)

                # Copy multiple messages at once
                await app.copy_messages(to_chat, from_chat, [1, 2, 3])
        """
        is_iterable = not isinstance(message_ids, int)
        ids = list(message_ids) if is_iterable else [message_ids]

        messages = await self.get_messages(from_chat_id, ids)
        if not isinstance(messages, list):
            messages = [messages]

        copied = []
        for message in messages:
            sent = await message.copy(
                chat_id=chat_id,
                message_thread_id=message_thread_id,
                disable_notification=disable_notification,
                protect_content=protect_content,
                caption="" if remove_caption else None,
                direct_messages_topic_id=direct_messages_topic_id,
            )
            copied.append(sent)

        return types.List(copied)
