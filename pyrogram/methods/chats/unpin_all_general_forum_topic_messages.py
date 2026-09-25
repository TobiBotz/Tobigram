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

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pyrogram


class UnpinAllGeneralForumTopicMessages:
    async def unpin_all_general_forum_topic_messages(
        self: pyrogram.Client, chat_id: int | str
    ) -> bool:
        """Clear the list of pinned messages in the General forum topic.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

        Returns:
            ``bool``: True on success.

        Example:
            .. code-block:: python

                await app.unpin_all_general_forum_topic_messages(chat_id)
        """
        return await self.unpin_all_chat_messages(chat_id=chat_id, top_msg_id=1)
