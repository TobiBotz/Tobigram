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

import io
import os
import re
from datetime import datetime
from typing import Union, BinaryIO, List, Optional, Callable

import pyrogram
from pyrogram import StopTransmission, enums
from pyrogram import raw
from pyrogram import types
from pyrogram import utils
from pyrogram.errors import FilePartMissing
from pyrogram.file_id import FileType


class SendVideo:
    async def send_video(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        video: Union[str, BinaryIO],
        caption: str = "",
        parse_mode: Optional["enums.ParseMode"] = None,
        caption_entities: Optional[List["types.MessageEntity"]] = None,
        has_spoiler: Optional[bool] = None,
        ttl_seconds: Optional[int] = None,
        duration: int = 0,
        width: int = 0,
        height: int = 0,
        thumb: Optional[Union[str, BinaryIO]] = None,
        file_name: Optional[str] = None,
        supports_streaming: bool = True,
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
        message_thread_id: Optional[int] = None,
        direct_messages_topic_id: Optional[int] = None,
        effect_id: Optional[int] = None,
        show_caption_above_media: Optional[bool] = None,
        video_start_timestamp: Optional[int] = None,
        video_cover: Optional[Union[str, BinaryIO]] = None,
        no_sound: Optional[bool] = None,
        reply_parameters: Optional["types.ReplyParameters"] = None,
        repeat_period: Optional[int] = None,
        business_connection_id: Optional[str] = None,
        allow_paid_broadcast: Optional[bool] = None,
        paid_message_star_count: Optional[int] = None,
        suggested_post_parameters: Optional["types.SuggestedPostParameters"] = None,
        rich_text: Optional[str] = None,
        rich_text_parse_mode: "enums.ParseMode" = enums.ParseMode.MARKDOWN,
        quote_text: Optional[str] = None,
        quote_entities: Optional[List["types.MessageEntity"]] = None,
        background: Optional[bool] = None,
        clear_draft: Optional[bool] = None,
        update_stickersets_order: Optional[bool] = None,
        send_as: Optional[Union[int, str]] = None,
        quick_reply_shortcut: Optional[int] = None,
        progress: Optional[Callable] = None,
        progress_args: tuple = ()
    ) -> Optional["types.Message"]:
        """Send video files.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).

            video (``str`` | ``BinaryIO``):
                Video to send.
                Pass a file_id as string to send a video that exists on the Telegram servers,
                pass an HTTP URL as a string for Telegram to get a video from the Internet,
                pass a file path as string to upload a new video that exists on your local machine, or
                pass a binary file-like object with its attribute ".name" set for in-memory uploads.

            caption (``str``, *optional*):
                Video caption, 0-1024 characters.

            parse_mode (:obj:`~pyrogram.enums.ParseMode`, *optional*):
                By default, texts are parsed using both Markdown and HTML styles.
                You can combine both syntaxes together.

            caption_entities (List of :obj:`~pyrogram.types.MessageEntity`):
                List of special entities that appear in the caption, which can be specified instead of *parse_mode*.

            rich_text (``str``, *optional*):
                Rich text content with GitHub Flavored Markdown or HTML formatting (server-side rendered).
                When provided, *caption*/*parse_mode*/*caption_entities* are ignored.

            rich_text_parse_mode (``str``, *optional*):
                Parse mode for *rich_text*: ``"markdown"`` (default, supports GFM) or ``"html"``.

            has_spoiler (``bool``, *optional*):
                Pass True if the video needs to be covered with a spoiler animation.

            ttl_seconds (``int``, *optional*):
                Self-Destruct Timer.
                If you set a timer, the video will self-destruct in *ttl_seconds*
                seconds after it was viewed.

            duration (``int``, *optional*):
                Duration of sent video in seconds.

            width (``int``, *optional*):
                Video width.

            height (``int``, *optional*):
                Video height.

            thumb (``str`` | ``BinaryIO``, *optional*):
                Thumbnail of the video sent.
                The thumbnail should be in JPEG format and less than 200 KB in size.
                A thumbnail's width and height should not exceed 320 pixels.
                Thumbnails can't be reused and can be only uploaded as a new file.

            video_cover (``str`` | ``BinaryIO``, *optional*):
                Cover for the video in the message.
                Pass a file_path, BinaryIO, file_id, or HTTP URL.
                The cover is uploaded as a photo and used as the video thumbnail.

            video_start_timestamp (``int``, *optional*):
                Video startpoint, in seconds.

            file_name (``str``, *optional*):
                File name of the video sent.
                Defaults to file's path basename.

            supports_streaming (``bool``, *optional*):
                Pass True, if the uploaded video is suitable for streaming.
                Defaults to True.

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            reply_to_message_id (``int``, *optional*):
                If the message is a reply, ID of the original message.

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
            :obj:`~pyrogram.types.Message` | ``None``: On success, the sent video message is returned, otherwise, in
            case the upload is deliberately stopped with :meth:`~pyrogram.Client.stop_transmission`, None is returned.

        Example:
            .. code-block:: python

                # Send video by uploading from local file
                await app.send_video("me", "video.mp4")

                # Add caption to the video
                await app.send_video("me", "video.mp4", caption="video caption")

                # Send self-destructing video
                await app.send_video("me", "video.mp4", ttl_seconds=10)

                # Keep track of the progress while uploading
                async def progress(current, total):
                    print(f"{current * 100 / total:.1f}%")

                await app.send_video("me", "video.mp4", progress=progress)
        """
        coverfile = None
        if video_cover is not None:
            is_bytes_io = isinstance(video_cover, io.BytesIO)
            is_uploaded_file = is_bytes_io or os.path.isfile(video_cover)
            is_external_url = not is_uploaded_file and re.match("^https?://", video_cover)

            if is_bytes_io and not hasattr(video_cover, "name"):
                video_cover.name = "cover.jpg"

            if is_uploaded_file:
                r = await self.invoke(
                    raw.functions.messages.UploadMedia(
                        business_connection_id=business_connection_id,
                        peer=await self.resolve_peer(chat_id),
                        media=raw.types.InputMediaUploadedPhoto(
                            file=await self.save_file(video_cover)
                        )
                    )
                )
                coverfile = raw.types.InputPhoto(
                    id=r.photo.id,
                    access_hash=r.photo.access_hash,
                    file_reference=r.photo.file_reference
                )
            elif is_external_url:
                r = await self.invoke(
                    raw.functions.messages.UploadMedia(
                        business_connection_id=business_connection_id,
                        peer=await self.resolve_peer(chat_id),
                        media=raw.types.InputMediaPhotoExternal(
                            url=video_cover
                        )
                    )
                )
                coverfile = raw.types.InputPhoto(
                    id=r.photo.id,
                    access_hash=r.photo.access_hash,
                    file_reference=r.photo.file_reference
                )
            else:
                coverfile = (utils.get_input_media_from_file_id(video_cover, FileType.PHOTO)).id

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
            if isinstance(video, str):
                if os.path.isfile(video):
                    thumb = await self.save_file(thumb)
                    file = await self.save_file(video, progress=progress, progress_args=progress_args)

                    media = raw.types.InputMediaUploadedDocument(
                        mime_type=self.guess_mime_type(video) or "video/mp4",
                        file=file,
                        ttl_seconds=ttl_seconds,
                        spoiler=has_spoiler,
                        nosound_video=no_sound,
                        thumb=thumb,
                        video_cover=coverfile,
                        video_timestamp=video_start_timestamp,
                        attributes=[
                            raw.types.DocumentAttributeVideo(
                                supports_streaming=supports_streaming if supports_streaming is not None else None,
                                duration=duration,
                                w=width,
                                h=height,
                                nosound=no_sound,
                                video_start_ts=video_start_timestamp
                            ),
                            raw.types.DocumentAttributeFilename(file_name=file_name or os.path.basename(video))
                        ]
                    )
                elif re.match("^https?://", video):
                    media = raw.types.InputMediaDocumentExternal(
                        url=video,
                        ttl_seconds=ttl_seconds,
                        spoiler=has_spoiler,
                        video_cover=coverfile,
                        video_timestamp=video_start_timestamp
                    )
                else:
                    media = utils.get_input_media_from_file_id(
                        video, FileType.VIDEO, ttl_seconds=ttl_seconds,
                        video_cover=coverfile,
                        video_start_timestamp=video_start_timestamp
                    )
            else:
                thumb = await self.save_file(thumb)
                file = await self.save_file(video, progress=progress, progress_args=progress_args)

                media = raw.types.InputMediaUploadedDocument(
                    mime_type=self.guess_mime_type(file_name or video.name) or "video/mp4",
                    file=file,
                    ttl_seconds=ttl_seconds,
                    spoiler=has_spoiler,
                    nosound_video=no_sound,
                    thumb=thumb,
                    video_cover=coverfile,
                    video_timestamp=video_start_timestamp,
                    attributes=[
                        raw.types.DocumentAttributeVideo(
                            supports_streaming=supports_streaming if supports_streaming is not None else None,
                            duration=duration,
                            w=width,
                            h=height,
                            nosound=no_sound,
                            video_start_ts=video_start_timestamp
                        ),
                        raw.types.DocumentAttributeFilename(file_name=file_name or video.name)
                    ]
                )

            while True:
                try:
                    if rich_text is not None:
                        if rich_text_parse_mode == enums.ParseMode.HTML:
                            rich_msg = raw.types.InputRichMessageHTML(
                                html=rich_text,
                            )
                        else:
                            rich_msg = raw.types.InputRichMessageMarkdown(
                                markdown=rich_text,
                            )
                        text_params = {"message": "", "entities": None}
                    else:
                        text_params = await utils.parse_text_entities(self, caption, parse_mode, caption_entities)

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
                            invert_media=show_caption_above_media if show_caption_above_media is not None else None,
                            schedule_repeat_period=repeat_period,
                            allow_paid_floodskip=allow_paid_broadcast if allow_paid_broadcast is not None else None,
                            allow_paid_stars=paid_message_star_count if paid_message_star_count is not None else None,
                            suggested_post=suggested_post_parameters.write() if suggested_post_parameters else None,
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
                    await self.save_file(video, file_id=file.id, file_part=e.value)
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
