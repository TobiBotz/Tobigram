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

from typing import Optional, Union

import pyrogram
from pyrogram import raw


class SendReaction:
    async def send_reaction(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        message_id: Optional[int] = None,
        emoji: str = "",
        big: bool = False,
        add_to_recent: bool = False,
        business_connection_id: Optional[str] = None,
        story_id: Optional[int] = None
    ) -> bool:
        """Send a reaction to a message.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            message_id (``int``):
                Identifier of the message.

            emoji (``str``, *optional*):
                Reaction emoji.
                Pass "" as emoji (default) to retract the reaction.
            
            big (``bool``, *optional*):
                Pass True to show a bigger and longer reaction.
                Defaults to False.

            business_connection_id (``str``, *optional*):
                Unique identifier of the business connection.
                Defaults to None.

            story_id (``int``, *optional*):
                Identifier of the story to react to, instead of a message.

            add_to_recent (``bool``, *optional*):
                Pass True to add the chosen reaction to the recently used ones.

        Returns:
            ``bool``: On success, True is returned.

        Example:
            .. code-block:: python

                # Send a reaction
                await app.send_reaction(chat_id, message_id, "🔥")

                # Retract a reaction
                await app.send_reaction(chat_id, message_id)
        """
        if message_id is None and story_id is None:
            raise ValueError("You must pass either message_id or story_id")

        reaction = [raw.types.ReactionEmoji(emoticon=emoji)] if emoji else None

        if story_id is not None:
            await self.invoke(
                raw.functions.stories.SendReaction(
                    peer=await self.resolve_peer(chat_id),
                    story_id=story_id,
                    reaction=reaction[0] if reaction else raw.types.ReactionEmpty(),
                    add_to_recent=add_to_recent
                )
            )

            return True

        await self.invoke(
            raw.functions.messages.SendReaction(
                peer=await self.resolve_peer(chat_id),
                msg_id=message_id,
                reaction=reaction,
                big=big,
                add_to_recent=add_to_recent
            ),
            business_connection_id=business_connection_id
        )

        return True