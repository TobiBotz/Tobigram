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


class RepostStory:
    async def repost_story(
        self: pyrogram.Client,
        from_chat_id: int | str,
        from_story_id: int,
        chat_id: int | str = "me",
        business_connection_id: str | None = None,
        active_period: int | None = None,
        post_to_chat_page: bool | None = None,
        protect_content: bool | None = None,
    ) -> types.Story | None:
        """Repost a story on behalf of a user or business account.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            from_chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the chat where the story was originally posted.

            from_story_id (``int``):
                Identifier of the story to repost.

            chat_id (``int`` | ``str``, *optional*):
                Unique identifier of target chat where to repost story. Defaults to "me".

            business_connection_id (``str``, *optional*):
                Unique identifier of the business connection on behalf of which the story will be reposted.

            active_period (``int``, *optional*):
                Period after which the story is moved to archive, in seconds.

            post_to_chat_page (``bool``, *optional*):
                Pass True to post the story to the chat page.

            protect_content (``bool``, *optional*):
                Protects the contents of the sent story from forwarding and saving.

        Returns:
            :obj:`~pyrogram.types.Story`: On success, the reposted story is returned.

        Example:
            .. code-block:: python

                story = await app.repost_story(from_chat_id="channel", from_story_id=12)
        """
        peer = await self.resolve_peer(chat_id)
        from_peer = await self.resolve_peer(from_chat_id)

        r = await self.invoke(
            raw.functions.stories.SendStory(
                peer=peer,
                media=raw.types.InputMediaEmpty(),
                privacy_rules=[raw.types.InputPrivacyValueAllowAll()],
                random_id=self.rnd_id(),
                fwd_from_id=from_peer,
                fwd_from_story=from_story_id,
                period=active_period,
                noforwards=protect_content,
                pinned=post_to_chat_page,
            ),
            business_connection_id=business_connection_id,
        )

        for i in r.updates:
            if isinstance(i, raw.types.UpdateStory):
                return await types.Story._parse(
                    self,
                    i.story,
                    i.peer,
                    {u.id: u for u in r.users},
                    {c.id: c for c in r.chats},
                )

        return None
