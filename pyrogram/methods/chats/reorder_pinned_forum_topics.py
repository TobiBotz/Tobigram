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


class ReorderPinnedForumTopics:
    async def reorder_pinned_forum_topics(
        self: pyrogram.Client,
        chat_id: int | str,
        order: list[int],
        force: bool | None = None,
    ) -> bool:
        """Reorder pinned forum topics in a forum supergroup.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            order (List of ``int``):
                List of topic IDs in the desired order.

            force (``bool``, *optional*):
                Pass True to overwrite the entire server-side pinned topic list.
                Defaults to None.

        Returns:
            ``bool``: On success, True is returned.

        Example:
            .. code-block:: python

                await app.reorder_pinned_forum_topics(chat_id, [123, 456])
        """
        await self.invoke(
            raw.functions.messages.ReorderPinnedForumTopics(
                peer=await self.resolve_peer(chat_id),
                order=order,
                force=force,
            )
        )

        return True
