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


class SendStoryReaction:
    async def send_story_reaction(
        self: pyrogram.Client,
        chat_id: int | str,
        story_id: int,
        emoji: int | str | None = None,
        add_to_recent: bool = False,
    ) -> bool:
        """React to a story.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            story_id (``int``):
                Identifier of the story to react to.

            emoji (``int`` | ``str``, *optional*):
                Reaction emoji. An int is the document id of a custom emoji.
                Pass None as emoji (default) to retract the reaction.

            add_to_recent (``bool``, *optional*):
                Pass True to add the chosen reaction to the recently used ones.
                Defaults to False.

        Returns:
            ``bool``: On success, True is returned.

        Example:
            .. code-block:: python

                # Send a reaction to a story
                await app.send_story_reaction(chat_id, story_id, "🔥")

                # Retract a reaction from a story
                await app.send_story_reaction(chat_id, story_id)
        """
        reaction: raw.base.Reaction
        if emoji is None:
            reaction = raw.types.ReactionEmpty()
        elif isinstance(emoji, int):
            reaction = raw.types.ReactionCustomEmoji(document_id=emoji)
        else:
            reaction = raw.types.ReactionEmoji(emoticon=emoji)

        await self.invoke(
            raw.functions.stories.SendReaction(
                peer=await self.resolve_peer(chat_id),
                story_id=story_id,
                reaction=reaction,
                add_to_recent=add_to_recent,
            )
        )

        return True
