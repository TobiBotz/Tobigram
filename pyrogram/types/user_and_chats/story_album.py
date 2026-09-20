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

from collections.abc import AsyncGenerator

import pyrogram
from pyrogram import raw, types

from ..object import Object
from ..update import Update


class StoryAlbum(Object, Update):
    """A story album (highlight).

    Parameters:
        id (``int``):
            Unique album identifier.

        title (``str``):
            Title of the album.

        photo (:obj:`~pyrogram.types.Photo`, *optional*):
            Album cover photo, if available.

        video (:obj:`~pyrogram.types.Document`, *optional*):
            Album cover video/animation, if available.

        chat (:obj:`~pyrogram.types.Chat`, *optional*):
            Chat where this story album belongs.
    """

    def __init__(
        self,
        *,
        client: pyrogram.Client | None = None,
        id: int,
        title: str,
        photo: types.Photo | None = None,
        video: types.Document | None = None,
        chat: types.Chat | None = None,
    ):
        super().__init__(client)

        self.id = id
        self.title = title
        self.photo = photo
        self.video = video
        self.chat = chat

    @staticmethod
    def _parse(
        client: pyrogram.Client,
        album: raw.types.StoryAlbum,
        chat: types.Chat | None = None,
    ) -> StoryAlbum | None:
        if not album:
            return None

        photo = None
        if getattr(album, "icon_photo", None):
            photo = types.Photo._parse(client, album.icon_photo)

        video = None
        if getattr(album, "icon_video", None):
            video = types.Document._parse(client, album.icon_video)

        return StoryAlbum(
            client=client,
            id=album.album_id,
            title=album.title,
            photo=photo,
            video=video,
            chat=chat,
        )

    async def delete(self) -> bool:
        """Bound method *delete* of :obj:`~pyrogram.types.StoryAlbum`.

        Use as a shortcut for:

        .. code-block:: python

            await client.delete_story_album(
                chat_id=album.chat.id,
                album_id=album.id
            )

        Returns:
            ``bool``: On success, True is returned.
        """
        if not self.chat:
            raise ValueError("Chat information is missing for this story album.")

        return await self._client.delete_story_album(
            chat_id=self.chat.id,
            album_id=self.id,
        )

    async def update(
        self,
        title: str | None = None,
        delete_stories: list[int] | None = None,
        add_stories: list[int] | None = None,
        order: list[int] | None = None,
    ) -> StoryAlbum:
        """Bound method *update* of :obj:`~pyrogram.types.StoryAlbum`.

        Use as a shortcut for:

        .. code-block:: python

            await client.update_story_album(
                chat_id=album.chat.id,
                album_id=album.id,
                title="New Title"
            )

        Parameters:
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
        """
        if not self.chat:
            raise ValueError("Chat information is missing for this story album.")

        return await self._client.update_story_album(
            chat_id=self.chat.id,
            album_id=self.id,
            title=title,
            delete_stories=delete_stories,
            add_stories=add_stories,
            order=order,
        )

    async def get_stories(
        self,
        offset: int = 0,
        limit: int = 0,
    ) -> AsyncGenerator[types.Story, None]:
        """Bound method *get_stories* of :obj:`~pyrogram.types.StoryAlbum`.

        Use as a shortcut for:

        .. code-block:: python

            async for story in album.get_stories():
                print(story)

        Parameters:
            offset (``int``, *optional*):
                Offset for pagination.

            limit (``int``, *optional*):
                Maximum number of stories to return.

        Returns:
            ``Generator``: On success, a generator yielding :obj:`~pyrogram.types.Story` objects is returned.
        """
        if not self.chat:
            raise ValueError("Chat information is missing for this story album.")

        async for story in self._client.get_story_album_stories(
            chat_id=self.chat.id,
            album_id=self.id,
            offset=offset,
            limit=limit,
        ):
            yield story

    async def copy(
        self,
        chat_id: int | str,
        title: str | None = None,
    ) -> StoryAlbum:
        """Bound method *copy* of :obj:`~pyrogram.types.StoryAlbum`.

        Use as a shortcut for:

        .. code-block:: python

            await client.copy_story_album(
                chat_id=target_chat,
                from_chat_id=album.chat.id,
                album_id=album.id,
                title="New Title"
            )

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            title (``str``, *optional*):
                New title for the album. If not specified, the original title is kept.

        Returns:
            :obj:`~pyrogram.types.StoryAlbum`: On success, the copied story album is returned.
        """
        if not self.chat:
            raise ValueError("Chat information is missing for this story album.")

        return await self._client.copy_story_album(
            chat_id=chat_id,
            from_chat_id=self.chat.id,
            album_id=self.id,
            title=title or self.title,
        )
