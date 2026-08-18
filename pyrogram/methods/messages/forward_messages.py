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
from typing import Union, List, Iterable, Optional

import pyrogram
from pyrogram import raw, utils
from pyrogram import types


class ForwardMessages:
    async def forward_messages(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        from_chat_id: Union[int, str],
        message_ids: Union[int, Iterable[int]],
        disable_notification: Optional[bool] = None,
        schedule_date: Optional[datetime] = None,
        protect_content: Optional[bool] = None,
        message_thread_id: Optional[int] = None,
        hide_sender_name: Optional[bool] = None,
        hide_captions: Optional[bool] = None,
        background: Optional[bool] = None,
        effect: Optional[int] = None,
        send_as: Optional[Union[int, str]] = None,
        schedule_repeat_period: Optional[int] = None,
        allow_paid_broadcast: Optional[bool] = None,
        paid_message_star_count: Optional[int] = None,
        video_start_timestamp: Optional[int] = None,
        reply_parameters: Optional["types.ReplyParameters"] = None,
        quick_reply_shortcut: Optional[int] = None,
        suggested_post_parameters: Optional["types.SuggestedPostParameters"] = None,
        business_connection_id: Optional[str] = None,
        direct_messages_topic_id: Optional[int] = None,
        with_my_score: Optional[bool] = None,
    ) -> Union["types.Message", List["types.Message"]]:
        """Forward messages of any kind.

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

            message_ids (``int`` | Iterable of ``int``):
                An iterable of message identifiers in the chat specified in *from_chat_id* or a single message id.

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            schedule_date (:py:obj:`~datetime.datetime`, *optional*):
                Date when the message will be automatically sent.

            protect_content (``bool``, *optional*):
                Protects the contents of the sent message from forwarding and saving.

            video_start_timestamp (``int``, *optional*):
                Video startpoint, in seconds.

            message_thread_id (``int``, *optional*):
                Unique identifier of a message thread to which the message belongs.
                For supergroups only.

            hide_sender_name (``bool``, *optional*):
                If True, the original author of the message will not be shown.

            hide_captions (``bool``, *optional*):
                If True, the original media captions will be removed.

            background (``bool``, *optional*):
                If True, the message will be sent in background.

            effect (``int``, *optional*):
                Unique identifier of the effect to apply to the message.

            send_as (``int`` | ``str``, *optional*):
                Unique identifier (int) or username (str) of the chat or user to send the message on behalf of.

            schedule_repeat_period (``int``, *optional*):
                Period in seconds after which the message will be automatically resent.

            allow_paid_broadcast (``bool``, *optional*):
                If True, you will be allowed to send up to 1000 messages per second.
                Ignoring broadcasting limits for a fee of 0.1 Telegram Stars per message.
                The relevant Stars will be withdrawn from the bot's balance.
                For bots only.

            paid_message_star_count (``int``, *optional*):
                The number of Telegram Stars the user agreed to pay to send the messages.

            direct_messages_topic_id (``int``, *optional*):
                Unique identifier of the direct messages topic to forward into.

            with_my_score (``bool``, *optional*):
                Include the sender's game score when forwarding a game message.

        Returns:
            :obj:`~pyrogram.types.Message` | List of :obj:`~pyrogram.types.Message`: In case *message_ids* was not
            a list, a single message is returned, otherwise a list of messages is returned.

        Example:
            .. code-block:: python

                # Forward a single message
                await app.forward_messages(to_chat, from_chat, 123)

                # Forward multiple messages at once
                await app.forward_messages(to_chat, from_chat, [1, 2, 3])
        """

        is_iterable = not isinstance(message_ids, int)
        message_ids = list(message_ids) if is_iterable else [message_ids]

        r = await self.invoke(
            raw.functions.messages.ForwardMessages(
                to_peer=await self.resolve_peer(chat_id),
                from_peer=await self.resolve_peer(from_chat_id),
                id=message_ids,
                silent=disable_notification if disable_notification is not None else None,
                random_id=[self.rnd_id() for _ in message_ids],
                schedule_date=utils.datetime_to_timestamp(schedule_date),
                noforwards=protect_content,
                video_timestamp=video_start_timestamp,
                top_msg_id=message_thread_id,
                drop_author=hide_sender_name if hide_sender_name is not None else None,
                drop_media_captions=hide_captions if hide_captions is not None else None,
                background=background if background is not None else None,
                effect=effect,
                send_as=await self.resolve_peer(send_as) if send_as is not None else None,
                schedule_repeat_period=schedule_repeat_period,
                allow_paid_floodskip=allow_paid_broadcast if allow_paid_broadcast is not None else None,
                allow_paid_stars=paid_message_star_count if paid_message_star_count is not None else None,
                reply_to=await utils.get_reply_to(
                    self,
                    reply_parameters,
                    message_thread_id,
                    direct_messages_topic_id=direct_messages_topic_id
                ),
                suggested_post=suggested_post_parameters.write() if suggested_post_parameters else None,
                with_my_score=with_my_score,
                quick_reply_shortcut=raw.types.InputQuickReplyShortcutId(shortcut_id=quick_reply_shortcut) if quick_reply_shortcut is not None else None,
            ),
            sleep_threshold=60,
            business_connection_id=business_connection_id
        )

        forwarded_messages = []

        users = {i.id: i for i in r.users}
        chats = {i.id: i for i in r.chats}

        for i in r.updates:
            if isinstance(i, (raw.types.UpdateNewMessage,
                              raw.types.UpdateNewChannelMessage,
                              raw.types.UpdateNewScheduledMessage)):
                forwarded_messages.append(
                    await types.Message._parse(
                        self, i.message,
                        users, chats
                    )
                )

        return types.List(forwarded_messages) if is_iterable else forwarded_messages[0]
