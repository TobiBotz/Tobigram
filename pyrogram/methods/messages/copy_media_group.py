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


class CopyMediaGroup:
    async def copy_media_group(
        self: pyrogram.Client,
        chat_id: int | str,
        from_chat_id: int | str,
        message_id: int,
        captions: list[str] | str | None = None,
        disable_notification: bool | None = None,
        reply_to_message_id: int | None = None,
        schedule_date: datetime | timedelta | None = None,
        protect_content: bool | None = None,
        effect_id: int | None = None,
        show_caption_above_media: bool | None = None,
        reply_parameters: types.ReplyParameters | None = None,
        message_thread_id: int | None = None,
        direct_messages_topic_id: int | None = None,
        allow_paid_broadcast: bool | None = None,
        paid_message_star_count: int | None = None,
        background: bool | None = None,
        clear_draft: bool | None = None,
        update_stickersets_order: bool | None = None,
        send_as: int | str | None = None,
        quick_reply_shortcut: int | None = None,
        business_connection_id: str | None = None,
        has_spoilers: bool | None = None,
    ) -> list[types.Message]:
        """Copy a media group by providing one of the message ids.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).

            from_chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the source chat where the original media group was sent.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).

            message_id (``int``):
                Message identifier in the chat specified in *from_chat_id*.

            captions (``str`` | List of ``str`` , *optional*):
                New caption for media, 0-1024 characters after entities parsing for each media.
                If not specified, the original caption is kept.
                Pass "" (empty string) to remove the caption.

                If a ``string`` is passed, it becomes a caption only for the first media.
                If a list of ``string`` passed, each element becomes caption for each media element.
                You can pass ``None`` in list to keep the original caption (see examples below).

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            reply_to_message_id (``int``, *optional*):
                If the message is a reply, ID of the original message.

            schedule_date (:py:obj:`~datetime.datetime`, *optional*):
                Date when the message will be automatically sent.

            protect_content (``bool``, *optional*):
                Protects the contents of the sent message from forwarding and saving.

            effect_id (``int`` ``64-bit``, *optional*):
                Unique identifier of the message effect to be added to the message; for private chats only.

            show_caption_above_media (``bool``, *optional*):
                Pass True, if the caption must be shown above the message media.

            reply_parameters (:obj:`~pyrogram.types.ReplyParameters`, *optional*):
                Describes reply parameters for the message that is being sent.

            message_thread_id (``int``, *optional*):
                Unique identifier of a message thread to which the message belongs.

            direct_messages_topic_id (``int``, *optional*):
                Unique identifier of the topic in a channel direct messages chat administered by the current user.

            allow_paid_broadcast (``bool``, *optional*):
                If True, you will be allowed to send up to 1000 messages per second.

            paid_message_star_count (``int``, *optional*):
                The number of Telegram Stars the user agreed to pay to send the messages.

            background (``bool``, *optional*):
                Pass True if the message is a background message.

            clear_draft (``bool``, *optional*):
                Pass True if the message draft should be cleared.

            update_stickersets_order (``bool``, *optional*):
                Pass True if the stickersets order should be updated.

            send_as (``int`` | ``str``, *optional*):
                Unique identifier (int) or username (str) of the chat to send the message as.

            quick_reply_shortcut (``int``, *optional*):
                Unique identifier of the quick reply shortcut.

            has_spoilers (``bool``, *optional*):
                Pass True to cover the copied media with a spoiler animation.

            business_connection_id (``str``, *optional*):
                Unique identifier of the business connection.

        Returns:
            List of :obj:`~pyrogram.types.Message`: On success, a list of copied messages is returned.

        Example:
            .. code-block:: python

                # Copy a media group
                await app.copy_media_group(to_chat, from_chat, 123)

                await app.copy_media_group(to_chat, from_chat, 123, captions="single caption")

                await app.copy_media_group(to_chat, from_chat, 123,
                    captions=["caption 1", None, ""])
        """

        if reply_parameters is None and reply_to_message_id is not None:
            reply_parameters = types.ReplyParameters(message_id=reply_to_message_id)

        media_group = await self.get_media_group(from_chat_id, message_id)
        multi_media = []

        for i, message in enumerate(media_group):
            if message.photo:
                file_id = message.photo.file_id
            elif message.audio:
                file_id = message.audio.file_id
            elif message.document:
                file_id = message.document.file_id
            elif message.video:
                file_id = message.video.file_id
            else:
                raise ValueError("Message with this type can't be copied.")

            media = utils.get_input_media_from_file_id(file_id=file_id, has_spoiler=has_spoilers)

            if isinstance(captions, list) and i < len(captions) and captions[i] is not None:
                text, entities = (await self.parser.parse(captions[i])).values()
            elif isinstance(captions, str):
                text, entities = (await self.parser.parse(captions if i == 0 else "")).values()
            elif message.caption and message.caption != "None":
                text, entities = (
                    await utils.parse_text_entities(
                        self, message.caption, None, message.caption_entities
                    )
                ).values()
            else:
                text, entities = "", None

            multi_media.append(
                raw.types.InputSingleMedia(
                    media=media, random_id=self.rnd_id(), message=text, entities=entities or None
                )
            )

        r = await self.invoke(
            raw.functions.messages.SendMultiMedia(
                peer=await self.resolve_peer(chat_id),
                multi_media=multi_media,
                silent=disable_notification if disable_notification is not None else None,
                reply_to=await utils.get_reply_to(
                    self,
                    reply_parameters,
                    message_thread_id,
                    direct_messages_topic_id=direct_messages_topic_id,
                ),
                schedule_date=utils.datetime_to_timestamp(schedule_date),
                noforwards=protect_content,
                effect=effect_id,
                invert_media=show_caption_above_media
                if show_caption_above_media is not None
                else None,
                allow_paid_floodskip=allow_paid_broadcast
                if allow_paid_broadcast is not None
                else None,
                allow_paid_stars=paid_message_star_count
                if paid_message_star_count is not None
                else None,
                background=background if background is not None else None,
                clear_draft=clear_draft if clear_draft is not None else None,
                update_stickersets_order=update_stickersets_order
                if update_stickersets_order is not None
                else None,
                send_as=await self.resolve_peer(send_as) if send_as is not None else None,
                quick_reply_shortcut=raw.types.InputQuickReplyShortcutId(
                    shortcut_id=quick_reply_shortcut
                )
                if quick_reply_shortcut is not None
                else None,
            ),
            sleep_threshold=60,
            business_connection_id=business_connection_id,
        )

        return await utils.parse_messages(
            self,
            raw.types.messages.Messages(
                messages=[
                    m.message
                    for m in filter(
                        lambda u: isinstance(
                            u,
                            (
                                raw.types.UpdateNewMessage,
                                raw.types.UpdateNewChannelMessage,
                                raw.types.UpdateNewScheduledMessage,
                            ),
                        ),
                        r.updates,
                    )
                ],
                topics=[],
                users=r.users,
                chats=r.chats,
            ),
        )
