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
from pyrogram import raw, types, utils


class GetStoryAlbumStories:
    async def get_story_album_stories(
        self: pyrogram.Client,
        chat_id: int | str,
        album_id: int,
        offset: int = 0,
        limit: int = 0,
    ) -> AsyncGenerator[types.Story, None]:
        """Get all stories in a story album (highlight).

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            album_id (``int``):
                ID of the album.

            offset (``int``, *optional*):
                Offset for pagination.

            limit (``int``, *optional*):
                Maximum number of stories to return.
                By default, all stories will be returned.

        Returns:
            ``Generator``: On success, a generator yielding :obj:`~pyrogram.types.Story` objects is returned.

        Example:
            .. code-block:: python

                async for story in app.get_story_album_stories(chat_id, album_id):
                    print(story)
        """
        current = 0
        total = abs(limit) or (1 << 31)
        chunk_limit = min(100, total)

        peer = await self.resolve_peer(chat_id)

        while True:
            r = await self.invoke(
                raw.functions.stories.GetAlbumStories(
                    peer=peer,
                    album_id=album_id,
                    offset=offset,
                    limit=chunk_limit,
                )
            )

            if not r.stories:
                return

            users = {i.id: i for i in r.users}
            chats = {i.id: i for i in r.chats}

            if isinstance(
                peer, (raw.types.InputPeerChannel, raw.types.InputPeerChannelFromMessage)
            ):
                peer_id = utils.get_raw_peer_id(peer)
                if peer_id not in chats:
                    channel = await self.invoke(
                        raw.functions.channels.GetChannels(id=[utils.get_input_channel(peer)])
                    )
                    chats.update({peer_id: channel.chats[0]})

            offset += len(r.stories)

            for story in r.stories:
                yield await types.Story._parse(self, story, peer, users, chats)

                current += 1

                if current >= total:
                    return
