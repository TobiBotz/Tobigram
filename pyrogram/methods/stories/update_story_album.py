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


class UpdateStoryAlbum:
    async def update_story_album(
        self: pyrogram.Client,
        chat_id: int | str,
        album_id: int,
        title: str | None = None,
        delete_stories: list[int] | None = None,
        add_stories: list[int] | None = None,
        order: list[int] | None = None,
    ) -> types.StoryAlbum:
        """Update a story album (highlight).

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            album_id (``int``):
                ID of the album to update.

            title (``str``, *optional*):
                New title for the album.

            delete_stories (List of ``int``, *optional*):
                List of story IDs to remove from the album.

            add_stories (List of ``int``, *optional*):
                List of story IDs to add to the album.

            order (List of ``int``, *optional*):
                New order of story IDs in the album.

        Returns:
            :obj:`~pyrogram.types.StoryAlbum`: On success, the updated story album is returned.

        Example:
            .. code-block:: python

                album = await app.update_story_album(
                    chat_id=chat_id,
                    album_id=album_id,
                    title="New Title",
                    add_stories=[4, 5]
                )
                print(album)
        """
        peer = await self.resolve_peer(chat_id)
        r = await self.invoke(
            raw.functions.stories.UpdateAlbum(
                peer=peer,
                album_id=album_id,
                title=title,
                delete_stories=delete_stories,
                add_stories=add_stories,
                order=order,
            )
        )

        chat = await self.get_chat(chat_id) if hasattr(self, "get_chat") else None

        return types.StoryAlbum._parse(self, r, chat=chat)
