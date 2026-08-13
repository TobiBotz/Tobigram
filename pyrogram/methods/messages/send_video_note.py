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

import os
from datetime import datetime
from typing import Union, BinaryIO, List, Optional, Callable

import pyrogram
from pyrogram import StopTransmission
from pyrogram import raw
from pyrogram import types
from pyrogram import utils
from pyrogram.errors import FilePartMissing
from pyrogram.file_id import FileType


class SendVideoNote:
    async def send_video_note(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        video_note: Union[str, BinaryIO],
        duration: int = 0,
        length: int = 1,
        thumb: Optional[Union[str, BinaryIO]] = None,
        disable_notification: Optional[bool] = None,
        reply_to_message_id: Optional[int] = None,
        reply_to_chat_id: Optional[Union[int, str]] = None,
        schedule_date: Optional[datetime] = None,
        protect_content: Optional[bool] = None,
        reply_markup: Optional[Union[
            "types.InlineKeyboardMarkup",
            "types.ReplyKeyboardMarkup",
            "types.ReplyKeyboardRemove",
            "types.ForceReply"
        ]] = None,
        quote_text: Optional[str] = None,
        quote_entities: Optional[List["types.MessageEntity"]] = None,
        reply_parameters: Optional["types.ReplyParameters"] = None,
        message_thread_id: Optional[int] = None,
        effect_id: Optional[int] = None,
        repeat_period: Optional[int] = None,
        business_connection_id: Optional[str] = None,
        allow_paid_broadcast: Optional[bool] = None,
        paid_message_star_count: Optional[int] = None,
        suggested_post_parameters: Optional["types.SuggestedPostParameters"] = None,
        direct_messages_topic_id: Optional[int] = None,
        show_caption_above_media: Optional[bool] = None,
        background: Optional[bool] = None,
        clear_draft: Optional[bool] = None,
        update_stickersets_order: Optional[bool] = None,
        send_as: Optional[Union[int, str]] = None,
        quick_reply_shortcut: Optional[int] = None,
        progress: Optional[Callable] = None,
        progress_args: tuple = (),
        **kwargs
    ) -> Optional["types.Message"]:
        """Send video messages.


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
                Sending video notes by a URL is currently unsupported.

            duration (``int``, *optional*):
                Duration of sent video in seconds.

            length (``int``, *optional*):
                Video width and height.

            thumb (``str`` | ``BinaryIO``, *optional*):
                Thumbnail of the video sent.
                The thumbnail should be in JPEG format and less than 200 KB in size.
                A thumbnail's width and height should not exceed 320 pixels.
                Thumbnails can't be reused and can be only uploaded as a new file.

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

        file = None

        try:
            if isinstance(video_note, str):
                if os.path.isfile(video_note):
                    thumb = await self.save_file(thumb)
                    file = await self.save_file(video_note, progress=progress, progress_args=progress_args)
                    media = raw.types.InputMediaUploadedDocument(
                        mime_type=self.guess_mime_type(video_note) or "video/mp4",
                        file=file,
                        thumb=thumb,
                        attributes=[
                            raw.types.DocumentAttributeVideo(
                                round_message=True,
                                duration=duration,
                                w=length,
                                h=length
                            )
                        ]
                    )
                else:
                    media = utils.get_input_media_from_file_id(video_note, FileType.VIDEO_NOTE)
            else:
                thumb = await self.save_file(thumb)
                file = await self.save_file(video_note, progress=progress, progress_args=progress_args)
                media = raw.types.InputMediaUploadedDocument(
                    mime_type=self.guess_mime_type(video_note.name) or "video/mp4",
                    file=file,
                    thumb=thumb,
                    attributes=[
                        raw.types.DocumentAttributeVideo(
                            round_message=True,
                            duration=duration,
                            w=length,
                            h=length
                        )
                    ]
                )

            while True:
                try:
                    text_params = {"message": ""}

                    r = await self.invoke(
                        raw.functions.messages.SendMedia(
                            peer=await self.resolve_peer(chat_id),
                            media=media,
                            silent=disable_notification if disable_notification is not None else None,
                            reply_to=await utils.get_reply_to(
                                self,
                                reply_parameters,
                                message_thread_id,
                                direct_messages_topic_id=direct_messages_topic_id
                            ),
                            random_id=self.rnd_id(),
                            schedule_date=utils.datetime_to_timestamp(schedule_date),
                            noforwards=protect_content,
                            effect=effect_id,
                            schedule_repeat_period=repeat_period,
                            allow_paid_floodskip=allow_paid_broadcast if allow_paid_broadcast is not None else None,
                            allow_paid_stars=paid_message_star_count if paid_message_star_count is not None else None,
                            suggested_post=suggested_post_parameters.write() if suggested_post_parameters else None,
                            invert_media=show_caption_above_media if show_caption_above_media is not None else None,
                            background=background,
                            clear_draft=clear_draft,
                            update_stickersets_order=update_stickersets_order,
                            send_as=await self.resolve_peer(send_as) if send_as is not None else None,
                            quick_reply_shortcut=raw.types.InputQuickReplyShortcutId(shortcut_id=quick_reply_shortcut) if quick_reply_shortcut is not None else None,
                            reply_markup=await reply_markup.write(self) if reply_markup else None,
                            **text_params
                        ),
                        sleep_threshold=60,
                        business_connection_id=business_connection_id
                    )
                except FilePartMissing as e:
                    await self.save_file(video_note, file_id=file.id, file_part=e.value)
                else:
                    for i in r.updates:
                        if isinstance(i, (raw.types.UpdateNewMessage,
                                          raw.types.UpdateNewChannelMessage,
                                          raw.types.UpdateNewScheduledMessage)):
                            return await types.Message._parse(
                                self, i.message,
                                {i.id: i for i in r.users},
                                {i.id: i for i in r.chats},
                                is_scheduled=isinstance(i, raw.types.UpdateNewScheduledMessage)
                            )
        except StopTransmission:
            return None
