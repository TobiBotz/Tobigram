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
from pyrogram import raw, types, utils
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime, timedelta


class SendInlineBotResult:
    async def send_inline_bot_result(
        self: pyrogram.Client,
        chat_id: int | str,
        query_id: int,
        result_id: str,
        disable_notification: bool | None = None,
        reply_parameters: types.ReplyParameters | None = None,
        reply_to_message_id: int | None = None,
        background: bool | None = None,
        clear_draft: bool | None = None,
        hide_via: bool | None = None,
        schedule_date: datetime | timedelta | None = None,
        send_as: int | str | None = None,
        quick_reply_shortcut: int | None = None,
        paid_message_star_count: int | None = None,
        business_connection_id: str | None = None,
        message_thread_id: int | None = None,
        direct_messages_topic_id: int | None = None,
    ) -> raw.base.Updates:
        """Send an inline bot result.
        Bot results can be retrieved using :meth:`~pyrogram.Client.get_inline_bot_results`

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).

            query_id (``int``):
                Unique identifier for the answered query.

            result_id (``str``):
                Unique identifier for the result that was chosen.

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            reply_to_message_id (``bool``, *optional*):
                If the message is a reply, ID of the original message.

            reply_parameters (:obj:`~pyrogram.types.ReplyParameters`, *optional*):
                Describes reply parameters for the message that is being sent.

            background (``bool``, *optional*):
                Send the message in background.

            clear_draft (``bool``, *optional*):
                Clear the draft of the chat.

            hide_via (``bool``, *optional*):
                Pass True to hide the "via @bot" header on the sent message.

            schedule_date (:py:obj:`~datetime.datetime`, *optional*):
                Date when the message will be automatically sent.

            send_as (``int`` | ``str``, *optional*):
                Unique identifier (int) or username (str) of the chat or channel to send the message as.

            quick_reply_shortcut (``int``, *optional*):
                Unique identifier of the quick reply shortcut the message belongs to.

            paid_message_star_count (``int``, *optional*):
                The number of Telegram Stars the user agreed to pay to send the messages.

            business_connection_id (``str``, *optional*):
                Unique identifier of the business connection.

            message_thread_id (``int``, *optional*):
                Unique identifier for a message thread in a forum topic.

            direct_messages_topic_id (``int``, *optional*):
                Unique identifier of the topic in a channel direct messages chat administered by the current user.
                For directs only only.

        Returns:
            :obj:`~pyrogram.raw.base.Updates`: Currently, on success, a raw result is returned.

        Example:
            .. code-block:: python

                await app.send_inline_bot_result(chat_id, query_id, result_id)
        """
        if reply_parameters is None and reply_to_message_id is not None:
            reply_parameters = types.ReplyParameters(
                message_id=reply_to_message_id,
            )

        return await self.invoke(
            raw.functions.messages.SendInlineBotResult(
                peer=await self.resolve_peer(chat_id),
                query_id=query_id,
                id=result_id,
                random_id=self.rnd_id(),
                silent=disable_notification if disable_notification is not None else None,
                reply_to=await utils.get_reply_to(
                    self, reply_parameters, message_thread_id, direct_messages_topic_id
                ),
                background=background if background is not None else None,
                clear_draft=clear_draft if clear_draft is not None else None,
                hide_via=hide_via if hide_via is not None else None,
                schedule_date=utils.datetime_to_timestamp(schedule_date),
                send_as=await self.resolve_peer(send_as) if send_as is not None else None,
                quick_reply_shortcut=raw.types.InputQuickReplyShortcutId(
                    shortcut_id=quick_reply_shortcut
                )
                if quick_reply_shortcut is not None
                else None,
                allow_paid_stars=paid_message_star_count
                if paid_message_star_count is not None
                else None,
            ),
            business_connection_id=business_connection_id,
        )
