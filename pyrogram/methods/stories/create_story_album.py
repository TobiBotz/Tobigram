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
from pyrogram import raw, types


class CreateStoryAlbum:
    async def create_story_album(
        self: pyrogram.Client,
        chat_id: int | str,
        title: str,
        stories: list[int],
    ) -> types.StoryAlbum:
        """Create a new story album (highlight).

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            title (``str``):
                Title of the album.

            stories (List of ``int``):
                List of story identifiers to include in the album.

        Returns:
            :obj:`~pyrogram.types.StoryAlbum`: On success, the created story album is returned.

        Example:
            .. code-block:: python

                album = await app.create_story_album(
                    chat_id="me",
                    title="Memories",
                    stories=[1, 2, 3]
                )
                print(album)
        """
        peer = await self.resolve_peer(chat_id)
        r = await self.invoke(
            raw.functions.stories.CreateAlbum(
                peer=peer,
                title=title,
                stories=stories,
            )
        )

        chat = await self.get_chat(chat_id) if hasattr(self, "get_chat") else None

        return types.StoryAlbum._parse(self, r, chat=chat)
