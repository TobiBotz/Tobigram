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


class GetStoriesViews:
    async def get_stories_views(
        self: pyrogram.Client,
        chat_id: int | str,
        story_ids: int | list[int],
    ) -> raw.types.stories.StoryViews:
        """Obtain view summary counts and reaction stats for multiple stories.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            story_ids (``int`` | List of ``int``):
                A single story identifier or a list of story identifiers.

        Returns:
            :obj:`~pyrogram.raw.types.stories.StoryViews`: On success, the story views summary object is returned.

        Example:
            .. code-block:: python

                views = await app.get_stories_views(chat_id, [1, 2, 3])
        """
        peer = await self.resolve_peer(chat_id)
        ids = [story_ids] if isinstance(story_ids, int) else list(story_ids)

        return await self.invoke(
            raw.functions.stories.GetStoriesViews(
                peer=peer,
                id=ids,
            )
        )
