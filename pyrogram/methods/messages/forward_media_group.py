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

from datetime import datetime
from typing import List, Union, Optional

import pyrogram
from pyrogram import raw, types, utils


class ForwardMediaGroup:
    async def forward_media_group(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        from_chat_id: Union[int, str],
        message_id: int,
        message_thread_id: Optional[int] = None,
        disable_notification: Optional[bool] = None,
        schedule_date: Optional[datetime] = None,
        hide_sender_name: Optional[bool] = None,
        hide_captions: Optional[bool] = None,
        protect_content: Optional[bool] = None,
        allow_paid_broadcast: Optional[bool] = None,
        reply_parameters: Optional["types.ReplyParameters"] = None,
        paid_message_star_count: Optional[int] = None,
        effect_id: Optional[int] = None,
        repeat_period: Optional[int] = None,
        background: Optional[bool] = None,
        send_as: Optional[Union[int, str]] = None,
        quick_reply_shortcut: Optional[int] = None,
        business_connection_id: Optional[str] = None,
    ) -> List["types.Message"]:
        """Forward a media group by providing one of the message ids.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).

            from_chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the source chat where the original message was sent.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).

            message_id (``int``):
                Message identifier in the chat specified in *from_chat_id*.

            message_thread_id (``int``, *optional*):
                Unique identifier of a message thread to which the message belongs.
                For supergroups only.

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            schedule_date (:py:obj:`~datetime.datetime`, *optional*):
                Date when the message will be automatically sent.

            hide_sender_name (``bool``, *optional*):
                If True, the original author of the message will not be shown.

            hide_captions (``bool``, *optional*):
                If True, the original media captions will be removed.

            protect_content (``bool``, *optional*):
                Protects the contents of the sent message from forwarding and saving.

            allow_paid_broadcast (``bool``, *optional*):
                If True, you will be allowed to send up to 1000 messages per second.
                Ignoring broadcasting limits for a fee of 0.1 Telegram Stars per message.
                The relevant Stars will be withdrawn from the bot's balance.
                For bots only.

            reply_parameters (:obj:`~pyrogram.types.ReplyParameters`, *optional*):
                Describes reply parameters for the message that is being sent.

            paid_message_star_count (``int``, *optional*):
                The number of Telegram Stars the user agreed to pay to send the messages.

            effect_id (``int`` ``64-bit``, *optional*):
                Unique identifier of the message effect to be added to the message; for private chats only.

            repeat_period (``int``, *optional*):
                Period after which the message will be sent again in seconds.

            background (``bool``, *optional*):
                Pass True if the message is a background message.

            send_as (``int`` | ``str``, *optional*):
                Unique identifier (int) or username (str) of the chat to send the message as.

            quick_reply_shortcut (``int``, *optional*):
                Unique identifier of the quick reply shortcut.

        Returns:
            List of :obj:`~pyrogram.types.Message`: On success, a list of forwarded messages is returned.

        Example:
            .. code-block:: python

                # Forward a media group
                await app.forward_media_group(to_chat, from_chat, 123)
        """
        message_ids = [i.id for i in await self.get_media_group(from_chat_id, message_id)]

        r = await self.invoke(
            raw.functions.messages.ForwardMessages(
                to_peer=await self.resolve_peer(chat_id),
                from_peer=await self.resolve_peer(from_chat_id),
                id=message_ids,
                silent=disable_notification if disable_notification is not None else None,
                random_id=[self.rnd_id() for _ in message_ids],
                schedule_date=utils.datetime_to_timestamp(schedule_date),
                drop_author=hide_sender_name if hide_sender_name is not None else None,
                drop_media_captions=hide_captions if hide_captions is not None else None,
                noforwards=protect_content,
                allow_paid_floodskip=allow_paid_broadcast if allow_paid_broadcast is not None else None,
                reply_to=await utils.get_reply_to(
                    client=self,
                    reply_parameters=reply_parameters,
                    message_thread_id=message_thread_id
                ),
                allow_paid_stars=paid_message_star_count if paid_message_star_count is not None else None,
                effect=effect_id,
                schedule_repeat_period=repeat_period,
                background=background if background is not None else None,
                send_as=await self.resolve_peer(send_as) if send_as is not None else None,
                quick_reply_shortcut=raw.types.InputQuickReplyShortcutId(shortcut_id=quick_reply_shortcut) if quick_reply_shortcut is not None else None,
                with_my_score=None,
                top_msg_id=message_thread_id,
                suggested_post=None,
                video_timestamp=None,
            ),
            sleep_threshold=60,
            business_connection_id=business_connection_id
        )

        return await utils.parse_messages(client=self, messages=r)
