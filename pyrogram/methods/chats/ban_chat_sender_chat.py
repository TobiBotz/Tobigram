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
from pyrogram import raw, utils


class BanChatSenderChat:
    async def ban_chat_sender_chat(
        self: pyrogram.Client,
        chat_id: int | str,
        sender_chat_id: int | str,
    ) -> bool:
        """Ban a channel chat from sending messages in a supergroup or channel.

        Use this to prevent a channel (acting as a sender) from posting in your chat.
        You must be an administrator with the appropriate admin rights.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target supergroup or channel
                where the sender chat should be banned.

            sender_chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the channel chat to ban.

        Returns:
            ``bool``: True on success.

        Example:
            .. code-block:: python

                # Ban a channel from sending in a supergroup
                await app.ban_chat_sender_chat(chat_id, sender_chat_id)
        """
        chat_peer = await self.resolve_peer(chat_id)
        sender_peer = await self.resolve_peer(sender_chat_id)

        await self.invoke(
            raw.functions.channels.EditBanned(
                channel=utils.get_input_channel(chat_peer),
                participant=sender_peer,
                banned_rights=raw.types.ChatBannedRights(
                    until_date=0,
                    view_messages=True,
                    send_messages=True,
                    send_media=True,
                    send_stickers=True,
                    send_gifs=True,
                    send_games=True,
                    send_inline=True,
                    embed_links=True,
                ),
            )
        )

        return True
