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

import os
from collections.abc import Callable
from datetime import datetime
from typing import BinaryIO

import pyrogram
from pyrogram import StopTransmission, raw, types, utils
from pyrogram.errors import FilePartMissing
from pyrogram.file_id import FileType

from ..ephemeral.as_ephemeral import as_ephemeral


class SendVideoNote:
    async def send_video_note(
        self: pyrogram.Client,
        chat_id: int | str,
        video_note: str | BinaryIO,
        duration: int = 0,
        length: int = 1,
        thumb: str | BinaryIO | None = None,
        view_once: bool | None = None,
        disable_notification: bool | None = None,
        reply_to_message_id: int | None = None,
        reply_to_chat_id: int | str | None = None,
        schedule_date: datetime | None = None,
        protect_content: bool | None = None,
        reply_markup: types.InlineKeyboardMarkup
        | types.ReplyKeyboardMarkup
        | types.ReplyKeyboardRemove
        | types.ForceReply
        | None = None,
        quote_text: str | None = None,
        quote_entities: list[types.MessageEntity] | None = None,
        reply_parameters: types.ReplyParameters | None = None,
        message_thread_id: int | None = None,
        effect_id: int | None = None,
        repeat_period: int | None = None,
        business_connection_id: str | None = None,
        allow_paid_broadcast: bool | None = None,
        paid_message_star_count: int | None = None,
        suggested_post_parameters: types.SuggestedPostParameters | None = None,
        direct_messages_topic_id: int | None = None,
        show_caption_above_media: bool | None = None,
        background: bool | None = None,
        clear_draft: bool | None = None,
        update_stickersets_order: bool | None = None,
        send_as: int | str | None = None,
        quick_reply_shortcut: int | None = None,
        progress: Callable | None = None,
        progress_args: tuple = (),
        ephemeral_message_parameters: types.EphemeralMessageParameters | None = None,
        **kwargs,
    ) -> types.Message | None:
        """Send video note files.


        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).

            video_note (``str`` | ``BinaryIO``):
                Video note to send.
                Pass a file_id as string to send a video note that exists on the Telegram servers,
                pass a file path as string to upload a new video note that exists on your local machine, or
                pass a binary file-like object with its attribute ".name" set for in-memory uploads.

            duration (``int``, *optional*):
                Duration of the video in seconds.

            length (``int``, *optional*):
                Video width and height.

            thumb (``str`` | ``BinaryIO``, *optional*):
                Thumbnail of the video sent.
                The thumbnail should be in JPEG format and less than 200 KB in size.
                A thumbnail's width and height should not exceed 320 pixels.
                Thumbnails can't be reused and can be only uploaded as a new file.

            view_once (``bool``, *optional*):
                Pass True if the video note must be opened once and disappear afterwards.
                Self-destructing media only works in private chats; a group or a
                channel drops the timer.

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            reply_to_message_id (``int``, *optional*):
                If the message is a reply, ID of the original message

            schedule_date (:py:obj:`~datetime.datetime`, *optional*):
                Date when the message will be automatically sent.

            protect_content (``bool``, *optional*):
                Protects the contents of the sent message from forwarding and saving.

            reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardRemove` | :obj:`~pyrogram.types.ForceReply`, *optional*):
                Additional interface options. An object for an inline keyboard, custom reply keyboard,
                instructions to remove reply keyboard or to force a reply from the user.

            progress (``Callable``, *optional*):
                Pass a callback function to view the file transmission progress.
                The function must take *(current, total)* as positional arguments (look at Other Parameters below for a
                detailed description) and will be called back each time a new file chunk has been successfully
                transmitted.

            progress_args (``tuple``, *optional*):
                Extra custom arguments for the progress callback function.
                You can pass anything you need to be available in the progress callback scope; for example, a Message
                object or a Client instance in order to edit the message with the updated progress status.

            ephemeral_message_parameters (:obj:`~pyrogram.types.EphemeralMessageParameters`, *optional*):
                Send the message as an ephemeral message, visible only to the user it
                names and absent from the chat's history, rather than as an ordinary one.
                The ephemeral RPC has no field for *silent*, *background*, *clear_draft*,
                *schedule_date*, *repeat_period*, *send_as*, *effect_id*,
                *quick_reply_shortcut*, *allow_paid_broadcast*,
                *paid_message_star_count*, *suggested_post_parameters* or
                *update_stickersets_order*; any of those that is set is logged and
                dropped.

            reply_to_chat_id (``int`` | ``str``, *optional*):
                Unique identifier for the chat to which the replied message belongs.
                Only applicable in combination with *reply_to_message_id*.

            quote_text (``str``, *optional*):
                Text of the quote to reply to.

            quote_entities (List of :obj:`~pyrogram.types.MessageEntity`):
                List of special entities that appear in *quote_text*, which can be specified instead of *parse_mode*.

            reply_parameters (:obj:`~pyrogram.types.ReplyParameters`, *optional*):
                Describes reply parameters for the message that is being sent.

            message_thread_id (``int``, *optional*):
                Unique identifier for a message thread in a forum topic.

            effect_id (``int``, *optional*):
                Unique identifier of the effect to apply to the message.

            repeat_period (``int``, *optional*):
                New period in seconds for the message to be sent repeatedly.

            business_connection_id (``str``, *optional*):
                Unique identifier of the business connection.

            allow_paid_broadcast (``bool``, *optional*):
                If True, you will be allowed to send up to 1000 messages per second.
                Ignoring broadcasting limits for a fee of 0.1 Telegram Stars per message.
                The relevant Stars will be withdrawn from the bot's balance.
                For bots only.

            paid_message_star_count (``int``, *optional*):
                The number of Telegram Stars the user agreed to pay to send the messages.

            suggested_post_parameters (:obj:`~pyrogram.types.SuggestedPostParameters`, *optional*):
                Parameters of the suggested post.

            direct_messages_topic_id (``int``, *optional*):
                Unique identifier of the topic in a channel direct messages chat administered by the current user.
                For directs only only.

            show_caption_above_media (``bool``, *optional*):
                Pass True, if the caption must be shown above the message media.

            background (``bool``, *optional*):
                Send the message in background.

            clear_draft (``bool``, *optional*):
                Clear the draft of the chat.

            update_stickersets_order (``bool``, *optional*):
                Move the sticker set to the top of the list.

            send_as (``int`` | ``str``, *optional*):
                Unique identifier (int) or username (str) of the chat or channel to send the message as.

            quick_reply_shortcut (``int``, *optional*):
                Unique identifier of the quick reply shortcut the message belongs to.

        Other Parameters:
            current (``int``):
                The amount of bytes transmitted so far.

            total (``int``):
                The total size of the file.

            *args (``tuple``, *optional*):
                Extra custom arguments as defined in the ``progress_args`` parameter.
                You can either keep ``*args`` or add every single extra argument in your function signature.

        Returns:
            :obj:`~pyrogram.types.Message` | ``None``: On success, the sent video note message is returned, otherwise,
            in case the upload is deliberately stopped with :meth:`~pyrogram.Client.stop_transmission`, None is
            returned.

        Example:
            .. code-block:: python

                # Send video note by uploading from local file
                await app.send_video_note("me", "video_note.mp4")

                # Set video note length
                await app.send_video_note("me", "video_note.mp4", length=25)
        """

        if kwargs:
            raise TypeError(f"Got unexpected keyword argument(s): {set(kwargs)}")
        if reply_parameters is None:
            if reply_to_message_id is not None:
                reply_parameters = types.ReplyParameters(
                    message_id=reply_to_message_id,
                    chat_id=reply_to_chat_id,
                    quote=quote_text,
                    quote_entities=quote_entities,
                )
            elif quote_text is not None:
                reply_parameters = types.ReplyParameters(
                    message_id=None,
                    chat_id=reply_to_chat_id,
                    quote=quote_text,
                    quote_entities=quote_entities,
                )

        ttl_seconds = (1 << 31) - 1 if view_once else None

        file = None

        try:
            if isinstance(video_note, str):
                if os.path.isfile(video_note):
                    thumb = await self.save_file(thumb)
                    file = await self.save_file(
                        video_note, progress=progress, progress_args=progress_args
                    )
                    media = raw.types.InputMediaUploadedDocument(
                        mime_type=self.guess_mime_type(video_note) or "video/mp4",
                        file=file,
                        thumb=thumb,
                        attributes=[
                            raw.types.DocumentAttributeVideo(
                                round_message=True, duration=duration, w=length, h=length
                            )
                        ],
                        ttl_seconds=ttl_seconds,
                    )
                else:
                    media = utils.get_input_media_from_file_id(
                        video_note, FileType.VIDEO_NOTE, ttl_seconds=ttl_seconds
                    )
            else:
                thumb = await self.save_file(thumb)
                file = await self.save_file(
                    video_note, progress=progress, progress_args=progress_args
                )
                media = raw.types.InputMediaUploadedDocument(
                    mime_type=self.guess_mime_type(
                        utils.get_file_name(video_note, fallback="video_note.mp4")
                    )
                    or "video/mp4",
                    file=file,
                    thumb=thumb,
                    attributes=[
                        raw.types.DocumentAttributeVideo(
                            round_message=True, duration=duration, w=length, h=length
                        )
                    ],
                    ttl_seconds=ttl_seconds,
                )

            while True:
                try:
                    text_params = {"message": ""}

                    r = await self.invoke(
                        await as_ephemeral(
                            self,
                            ephemeral_message_parameters,
                            raw.functions.messages.SendMedia(
                                peer=await self.resolve_peer(chat_id),
                                media=media,
                                silent=disable_notification,
                                reply_to=await utils.get_reply_to(
                                    self,
                                    reply_parameters,
                                    message_thread_id,
                                    direct_messages_topic_id=direct_messages_topic_id,
                                ),
                                random_id=self.rnd_id(),
                                schedule_date=utils.datetime_to_timestamp(schedule_date),
                                noforwards=protect_content,
                                effect=effect_id,
                                schedule_repeat_period=repeat_period,
                                allow_paid_floodskip=allow_paid_broadcast
                                if allow_paid_broadcast is not None
                                else None,
                                allow_paid_stars=paid_message_star_count
                                if paid_message_star_count is not None
                                else None,
                                suggested_post=suggested_post_parameters.write()
                                if suggested_post_parameters
                                else None,
                                invert_media=show_caption_above_media
                                if show_caption_above_media is not None
                                else None,
                                background=background,
                                clear_draft=clear_draft,
                                update_stickersets_order=update_stickersets_order,
                                send_as=await self.resolve_peer(send_as)
                                if send_as is not None
                                else None,
                                quick_reply_shortcut=raw.types.InputQuickReplyShortcutId(
                                    shortcut_id=quick_reply_shortcut
                                )
                                if quick_reply_shortcut is not None
                                else None,
                                reply_markup=await reply_markup.write(self)
                                if reply_markup
                                else None,
                                **text_params,
                            ),
                        ),
                        sleep_threshold=60,
                        business_connection_id=business_connection_id,
                    )
                except FilePartMissing as e:
                    await self.save_file(video_note, file_id=file.id, file_part=e.value)
                else:
                    for i in r.updates:
                        if isinstance(
                            i,
                            (
                                raw.types.UpdateNewMessage,
                                raw.types.UpdateNewChannelMessage,
                                raw.types.UpdateNewScheduledMessage,
                                raw.types.UpdateNewEphemeralMessage,
                            ),
                        ):
                            return await types.Message._parse(
                                self,
                                i.message,
                                {i.id: i for i in r.users},
                                {i.id: i for i in r.chats},
                                is_scheduled=isinstance(i, raw.types.UpdateNewScheduledMessage),
                            )

                    # a send that succeeded is never re-sent, whatever the answer carried
                    return None
        except StopTransmission:
            return None
