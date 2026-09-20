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
from pyrogram import types


class CopyStoryAlbum:
    async def copy_story_album(
        self: pyrogram.Client,
        chat_id: int | str,
        from_chat_id: int | str,
        album_id: int,
        title: str | None = None,
    ) -> types.StoryAlbum:
        """Copy all stories from a story album (highlight) to another chat and create a new album.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            from_chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the source chat where the original album is located.

            album_id (``int``):
                Identifier of the story album to copy.

            title (``str``, *optional*):
                New title for the album. If not specified, the original album title will be used.

        Returns:
            :obj:`~pyrogram.types.StoryAlbum`: On success, the newly created story album is returned.

        Example:
            .. code-block:: python

                # Copy a story album to another chat
                album = await app.copy_story_album(
                    chat_id="target_channel",
                    from_chat_id="source_channel",
                    album_id=123
                )
                print(album.title)
        """
        if title is None:
            albums = await self.get_story_albums(from_chat_id)
            for a in albums:
                if a.id == album_id:
                    title = a.title
                    break
            if not title:
                title = f"Album {album_id}"

        source_stories: list[types.Story] = []
        async for story in self.get_story_album_stories(from_chat_id, album_id):
            source_stories.append(story)

        new_story_ids: list[int] = []
        for story in source_stories:
            new_story = await story.copy(chat_id=chat_id)
            new_story_ids.append(new_story.id)

        return await self.create_story_album(
            chat_id=chat_id,
            title=title,
            stories=new_story_ids,
        )
