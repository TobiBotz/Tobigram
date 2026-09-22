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


class GetStoryReactionsList:
    async def get_story_reactions_list(
        self: pyrogram.Client,
        chat_id: int | str,
        story_id: int,
        offset: str | None = None,
        limit: int = 100,
        reaction: raw.base.Reaction | None = None,
        forwards_first: bool | None = None,
    ) -> raw.types.stories.StoryReactionsList:
        """Obtain the list of reactions sent to a specific story.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            story_id (``int``):
                Unique identifier of the story.

            offset (``str``, *optional*):
                Offset for results pagination.

            limit (``int``, *optional*):
                Maximum number of results to return. Defaults to 100.

            reaction (:obj:`~pyrogram.raw.base.Reaction`, *optional*):
                Filter by specific reaction.

            forwards_first (``bool``, *optional*):
                Whether to return forwards first.

        Returns:
            :obj:`~pyrogram.raw.types.stories.StoryReactionsList`: On success, reactions list object is returned.

        Example:
            .. code-block:: python

                reactions = await app.get_story_reactions_list(chat_id, 123)
        """
        peer = await self.resolve_peer(chat_id)

        return await self.invoke(
            raw.functions.stories.GetStoryReactionsList(
                peer=peer,
                id=story_id,
                offset=offset,
                limit=limit,
                reaction=reaction,
                forwards_first=forwards_first,
            )
        )
