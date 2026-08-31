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

from typing import Union, Optional

import pyrogram
from pyrogram import raw


class UnpinAllChatMessages:
    async def unpin_all_chat_messages(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        top_msg_id: Optional[int] = None,
        saved_peer_id: Optional[Union[int, str]] = None,
    ) -> bool:
        """Use this method to clear the list of pinned messages in a chat.
        If the chat is not a private chat, the bot must be an administrator in the chat for this to work and must have
        the 'can_pin_messages' admin right in a supergroup or 'can_edit_messages' admin right in a channel.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            top_msg_id (``int``, *optional*):
                Unique identifier of the forum topic the action is broadcast to.

            saved_peer_id (``int`` | ``str``, *optional*):
                Unique identifier (int) or username (str) of the dialog inside your personal
                cloud (Saved Messages) to act on, rather than the cloud as a whole.

        Returns:
            ``bool``: True on success.

        Example:
            .. code-block:: python

                # Unpin all chat messages
                await app.unpin_all_chat_messages(chat_id)
        """
        rpc = raw.functions.messages.UnpinAllMessages(
            peer=await self.resolve_peer(chat_id),
            top_msg_id=top_msg_id,
            saved_peer_id=(
                await self.resolve_peer(saved_peer_id)
                if saved_peer_id
                else None
            )
        )

        while (await self.invoke(rpc)).offset:
            pass

        return True
