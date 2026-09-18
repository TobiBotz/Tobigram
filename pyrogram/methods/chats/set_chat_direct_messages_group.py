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


import pyrogram
from pyrogram import raw


class SetChatDirectMessagesGroup:
    async def set_chat_direct_messages_group(
        self: "pyrogram.Client",
        chat_id: int | str,
        paid_message_star_count: int = 0,
        is_enabled: bool | None = None,
    ) -> bool:
        """Change the direct messages group settings of a channel.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target channel.

            paid_message_star_count (``int``, *optional*):
                Amount of Telegram Stars that must be paid for each message sent to the direct
                messages chat by a user who is not an administrator of the channel, 0-10000.
                Defaults to 0.

            is_enabled (``bool``, *optional*):
                Pass True to enable the direct messages group for the channel, False to disable it.

        Returns:
            ``bool``: On success, True is returned.

        Example:
            .. code-block:: python

                await app.set_chat_direct_messages_group(chat_id, is_enabled=True)
        """

        r = await self.invoke(
            raw.functions.channels.UpdatePaidMessagesPrice(
                channel=await self.resolve_peer(chat_id),
                send_paid_messages_stars=paid_message_star_count,
                broadcast_messages_allowed=is_enabled,
            )
        )

        return bool(r)
