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
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator


class GetMessageReactions:
    async def get_message_reactions(
        self: pyrogram.Client,
        chat_id: int | str,
        message_id: int,
        reaction: raw.base.Reaction | types.Reaction | str | int | None = None,
        limit: int = 0,
    ) -> AsyncGenerator[types.MessagePeerReaction, None] | None:
        """Get reactions added to a specific message.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            message_id (``int``):
                Identifier of the target message.

            reaction (``str`` | ``int`` | :obj:`~pyrogram.types.Reaction`, *optional*):
                Target reaction to filter by. Can be an emoji string (e.g. "👍"), a custom emoji ID (int),
                or a :obj:`~pyrogram.types.Reaction` object. Defaults to None (returns all reactions).

            limit (``int``, *optional*):
                Limits the number of reactions to be retrieved.
                By default, no limit is applied and all reactions are returned.

        Returns:
            ``Generator``: A generator yielding :obj:`~pyrogram.types.MessagePeerReaction` objects.

        Example:
            .. code-block:: python

                # Get all reactions on a message
                async for reaction in app.get_message_reactions(chat_id, message_id):
                    print(reaction.user.first_name, reaction.reaction)

                # Get only thumbs-up reactions
                async for reaction in app.get_message_reactions(chat_id, message_id, reaction="👍"):
                    print(reaction.user.first_name)
        """
        raw_reaction = None
        if isinstance(reaction, str):
            raw_reaction = raw.types.ReactionEmoji(emoticon=reaction)
        elif isinstance(reaction, int):
            raw_reaction = raw.types.ReactionCustomEmoji(document_id=reaction)
        elif isinstance(reaction, types.Reaction):
            if reaction.custom_emoji_id:
                raw_reaction = raw.types.ReactionCustomEmoji(document_id=reaction.custom_emoji_id)
            elif reaction.emoji:
                raw_reaction = raw.types.ReactionEmoji(emoticon=reaction.emoji)
        elif isinstance(reaction, raw.base.Reaction):
            raw_reaction = reaction

        current = 0
        total = abs(limit) or (1 << 31) - 1
        sub_limit = min(100, total)
        offset = None

        while True:
            r = await self.invoke(
                raw.functions.messages.GetMessageReactionsList(
                    peer=await self.resolve_peer(chat_id),
                    id=message_id,
                    reaction=raw_reaction,
                    offset=offset,
                    limit=sub_limit,
                ),
                sleep_threshold=60,
            )

            if not r.reactions:
                return

            users = {u.id: u for u in r.users}
            chats = {c.id: c for c in r.chats}

            for item in r.reactions:
                yield types.MessagePeerReaction._parse(self, item, users, chats)

                current += 1
                if current >= total:
                    return

            if not getattr(r, "next_offset", None):
                return

            offset = r.next_offset
