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

from typing import Union, Optional

import pyrogram
from pyrogram import raw, types


class CreateForumTopic:
    async def create_forum_topic(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        title: str,
        icon_color: Optional[int] = None,
        icon_emoji_id: Optional[int] = None,
        send_as: Optional[Union[int, str]] = None,
    ) -> "types.ForumTopicCreated":
        """Create a new forum topic.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            title (``str``):
                The forum topic title.

            icon_color (``int``, *optional*):
                The color of forum topic icon.

            icon_emoji_id (``int``, *optional*):
                Unique identifier of the custom emoji shown as the topic icon

            send_as (``int`` | ``str``, *optional*):
                Unique identifier (int) or username (str) of the chat or channel to
                create the topic as.

        Returns:
            :obj:`~pyrogram.types.ForumTopicCreated`: On success, a forum_topic_created object is returned.

        Example:
            .. code-block:: python

                await app.create_forum_topic(chat_id=chat_id, title="Topic Title")
        """
        r = await self.invoke(
            raw.functions.messages.CreateForumTopic(
                peer=await self.resolve_peer(chat_id),
                title=title,
                random_id=self.rnd_id(),
                icon_color=icon_color,
                icon_emoji_id=icon_emoji_id,
                send_as=await self.resolve_peer(send_as) if send_as is not None else None
            )
        )

        return types.ForumTopicCreated._parse(r.updates[1].message)

