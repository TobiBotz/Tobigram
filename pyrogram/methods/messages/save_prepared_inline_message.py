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


class SavePreparedInlineMessage:
    async def save_prepared_inline_message(
        self: pyrogram.Client,
        user_id: int | str,
        result: raw.base.InputBotInlineResult,
        allow_user_chats: bool | None = None,
        allow_bot_chats: bool | None = None,
        allow_group_chats: bool | None = None,
        allow_channel_chats: bool | None = None,
    ) -> raw.base.messages.BotPreparedInlineMessage:
        """Store a message that can be sent by a user of a Mini App.

        Use this method to prepare an inline result that a Mini App user can send to a chat
        via the ``web_app_send_prepared_message`` Web App event.

        .. include:: /_includes/usable-by/bots.rst

        Parameters:
            user_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the user who will send the message.

            result (:obj:`~pyrogram.raw.base.InputBotInlineResult`):
                The prepared inline result object to store.

            allow_user_chats (``bool``, *optional*):
                Pass True if the message can be sent to private chats with users.

            allow_bot_chats (``bool``, *optional*):
                Pass True if the message can be sent to private chats with bots.

            allow_group_chats (``bool``, *optional*):
                Pass True if the message can be sent to group and supergroup chats.

            allow_channel_chats (``bool``, *optional*):
                Pass True if the message can be sent to channel chats.

        Returns:
            :obj:`~pyrogram.raw.base.messages.BotPreparedInlineMessage`: The prepared inline message
            object containing the ``id`` and ``expiration date``.

        Example:
            .. code-block:: python

                from pyrogram.raw.types import InputBotInlineResultArticle, InputBotInlineMessageText

                result = InputBotInlineResultArticle(
                    id="unique_id",
                    title="Article Title",
                    input_message_content=InputBotInlineMessageText(message="Hello!"),
                )
                prepared = await app.save_prepared_inline_message(
                    user_id=user_id,
                    result=result,
                    allow_user_chats=True,
                )
        """
        peer_types = []

        if allow_user_chats:
            peer_types.append(raw.types.InlineQueryPeerTypePM())
        if allow_bot_chats:
            peer_types.append(raw.types.InlineQueryPeerTypeBotPM())
        if allow_group_chats:
            peer_types.append(raw.types.InlineQueryPeerTypeChat())
            peer_types.append(raw.types.InlineQueryPeerTypeMegagroup())
        if allow_channel_chats:
            peer_types.append(raw.types.InlineQueryPeerTypeBroadcast())

        user_peer = await self.resolve_peer(user_id)

        r = await self.invoke(
            raw.functions.messages.SavePreparedInlineMessage(
                result=result,
                user_id=user_peer,
                peer_types=peer_types if peer_types else None,
            )
        )

        return r
