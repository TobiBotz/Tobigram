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
from pyrogram import enums, raw, types, utils
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime, timedelta
    from collections.abc import AsyncGenerator


# noinspection PyShadowingBuiltins
async def get_chunk(
    client,
    chat_id: int | str,
    query: str = "",
    filter: enums.MessagesFilter = enums.MessagesFilter.EMPTY,
    offset: int = 0,
    limit: int = 100,
    from_user: int | str | None = None,
    saved_peer_id: int | str | None = None,
    top_msg_id: int | None = None,
    offset_id: int = 0,
    min_date: datetime | timedelta | None = None,
    max_date: datetime | timedelta | None = None,
    min_id: int = 0,
    max_id: int = 0,
) -> list[types.Message]:
    r = await client.invoke(
        raw.functions.messages.Search(
            peer=await client.resolve_peer(chat_id),
            q=query,
            filter=filter.value(),
            min_date=utils.datetime_to_timestamp(min_date) or 0,
            max_date=utils.datetime_to_timestamp(max_date) or 0,
            offset_id=offset_id,
            add_offset=offset,
            limit=limit,
            min_id=min_id,
            max_id=max_id,
            from_id=(await client.resolve_peer(from_user) if from_user else None),
            saved_peer_id=(await client.resolve_peer(saved_peer_id) if saved_peer_id else None),
            top_msg_id=top_msg_id,
            hash=0,
        ),
        sleep_threshold=60,
    )

    return await utils.parse_messages(client, r, replies=0)


class SearchMessages:
    # noinspection PyShadowingBuiltins
    async def search_messages(
        self: pyrogram.Client,
        chat_id: int | str,
        query: str = "",
        offset: int = 0,
        filter: enums.MessagesFilter = enums.MessagesFilter.EMPTY,
        limit: int = 0,
        from_user: int | str | None = None,
        saved_peer_id: int | str | None = None,
        top_msg_id: int | None = None,
        offset_id: int = 0,
        min_date: datetime | timedelta | None = None,
        max_date: datetime | timedelta | None = None,
        min_id: int = 0,
        max_id: int = 0,
    ) -> AsyncGenerator[types.Message, None] | None:
        """Search for text and media messages inside a specific chat.

        If you want to get the messages count only, see :meth:`~pyrogram.Client.search_messages_count`.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).

            query (``str``, *optional*):
                Text query string.
                Required for text-only messages, optional for media messages (see the ``filter`` argument).
                When passed while searching for media messages, the query will be applied to captions.
                Defaults to "" (empty string).

            offset (``int``, *optional*):
                Sequential number of the first message to be returned.
                Defaults to 0.

            filter (:obj:`~pyrogram.enums.MessagesFilter`, *optional*):
                Pass a filter in order to search for specific type of messages only.
                Defaults to :obj:`~pyrogram.enums.MessagesFilter.EMPTY` (search all messages).

            limit (``int``, *optional*):
                Limits the number of messages to be retrieved.
                By default, no limit is applied and all messages are returned.

            from_user (``int`` | ``str``, *optional*):
                Unique identifier (int) or username (str) of the target user you want to search messages from for
                groups and supergroups.

            saved_peer_id (``int`` | ``str``, *optional*):
                Unique identifier (int) or username (str) of the target chat you want to search messages from for
                your personal cloud (Saved Messages).

            top_msg_id (``int``, *optional*):
                Unique identifier of the forum topic the action is broadcast to.

            offset_id (``int``, *optional*):
                Identifier of the first message to be returned.

            min_date (:py:obj:`~datetime.datetime`, *optional*):
                Pass a date to return only messages sent on or after that date.

            max_date (:py:obj:`~datetime.datetime`, *optional*):
                Pass a date to return only messages sent on or before that date.

            min_id (``int``, *optional*):
                Identifier of the oldest message to be returned.

            max_id (``int``, *optional*):
                Identifier of the newest message to be returned.

        Returns:
            ``Generator``: A generator yielding :obj:`~pyrogram.types.Message` objects.

        Example:
            .. code-block:: python

                # Search for "hello" in chat
                async for message in app.search_messages(chat_id, query="hello"):
                    print(message.text)

                # Search for recent photos in chat
                async for message in app.search_messages(chat, filter=enums.MessagesFilter.PHOTO):
                    print(message.photo)

                # Search for messages containing "hello" sent by yourself in chat
                async for message in app.search_messages(chat, "hello", from_user="me"):
                    print(message.text)
        """

        current = 0
        total = abs(limit) or (1 << 31) - 1
        limit = min(100, total)

        while True:
            messages = await get_chunk(
                client=self,
                chat_id=chat_id,
                query=query,
                filter=filter,
                offset=offset,
                limit=limit,
                from_user=from_user,
                saved_peer_id=saved_peer_id,
                top_msg_id=top_msg_id,
                offset_id=offset_id,
                min_date=min_date,
                max_date=max_date,
                min_id=min_id,
                max_id=max_id,
            )

            if not messages:
                return

            offset += len(messages)

            for message in messages:
                yield message

                current += 1

                if current >= total:
                    return
