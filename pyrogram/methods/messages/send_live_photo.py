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

from typing import BinaryIO, TYPE_CHECKING

import pyrogram
from pyrogram import enums, raw, types, utils

from ..ephemeral.as_ephemeral import as_ephemeral

if TYPE_CHECKING:
    from datetime import datetime, timedelta
    from collections.abc import Callable


class SendLivePhoto:
    async def send_live_photo(
        self: pyrogram.Client,
        chat_id: int | str,
        live_photo: str | BinaryIO,
        photo: str | BinaryIO,
        caption: str = "",
        parse_mode: enums.ParseMode | None = None,
        caption_entities: list[types.MessageEntity] | None = None,
        has_spoiler: bool | None = None,
        width: int = 0,
        height: int = 0,
        disable_notification: bool | None = None,
        message_thread_id: int | None = None,
        direct_messages_topic_id: int | None = None,
        effect_id: int | None = None,
        show_caption_above_media: bool | None = None,
        reply_parameters: types.ReplyParameters | None = None,
        schedule_date: datetime | timedelta | None = None,
        repeat_period: int | None = None,
        protect_content: bool | None = None,
        business_connection_id: str | None = None,
        allow_paid_broadcast: bool | None = None,
        paid_message_star_count: int | None = None,
        suggested_post_parameters: types.SuggestedPostParameters | None = None,
        reply_markup: (
            types.InlineKeyboardMarkup
            | types.ReplyKeyboardMarkup
            | types.ReplyKeyboardRemove
            | types.ForceReply
            | None
        ) = None,
        ephemeral_message_parameters: types.EphemeralMessageParameters | None = None,
        progress: Callable | None = None,
        progress_args: tuple = (),
        **kwargs,
    ) -> types.Message | None:
        """Send a live photo, a still image paired with the short video it was taken with.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            live_photo (``str`` | ``BinaryIO``):
                Video part of the live photo, as a local path or a file-like object.

            photo (``str`` | ``BinaryIO``):
                Still part of the live photo, as a local path or a file-like object.

            caption (``str``, *optional*):
                Caption of the live photo, 0-1024 characters.

            parse_mode (:obj:`~pyrogram.enums.ParseMode`, *optional*):
                By default, texts are parsed using both Markdown and HTML styles.
                You can combine both syntaxes together.

            caption_entities (List of :obj:`~pyrogram.types.MessageEntity`, *optional*):
                List of special entities that appear in the caption, which can be specified instead of *parse_mode*.

            has_spoiler (``bool``, *optional*):
                Pass True if the live photo needs to be covered with a spoiler animation.

            width (``int``, *optional*):
                Width of the video part.

            height (``int``, *optional*):
                Height of the video part.

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            message_thread_id (``int``, *optional*):
                Unique identifier for the target message thread (topic) of the forum.

            direct_messages_topic_id (``int``, *optional*):
                Unique identifier of the direct messages topic.

            effect_id (``int``, *optional*):
                Unique identifier of the effect to apply to the message.

            show_caption_above_media (``bool``, *optional*):
                Pass True, if the caption must be shown above the message media.

            reply_parameters (:obj:`~pyrogram.types.ReplyParameters`, *optional*):
                Describes reply parameters for the message that is being sent.

            schedule_date (:py:obj:`~datetime.datetime`, *optional*):
                Date when the message will be automatically sent.

            repeat_period (``int``, *optional*):
                Period after which the message will be sent again in seconds.

            protect_content (``bool``, *optional*):
                Protects the contents of the sent message from forwarding and saving.

            business_connection_id (``str``, *optional*):
                Unique identifier of the business connection.

            allow_paid_broadcast (``bool``, *optional*):
                Pay to skip the broadcast flood limit.

            paid_message_star_count (``int``, *optional*):
                The number of Telegram Stars the user agreed to pay to send the message.

            suggested_post_parameters (:obj:`~pyrogram.types.SuggestedPostParameters`, *optional*):
                Parameters of the suggested post.

            reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardRemove` | :obj:`~pyrogram.types.ForceReply`, *optional*):
                Additional interface options. An object for an inline keyboard, custom reply keyboard,
                instructions to remove reply keyboard or to force a reply from the user.

            ephemeral_message_parameters (:obj:`~pyrogram.types.EphemeralMessageParameters`, *optional*):
                Parameters of the ephemeral message to send.

            progress (``Callable``, *optional*):
                Pass a callback function to view the file transmission progress.

            progress_args (``tuple``, *optional*):
                Extra custom arguments for the progress callback function.

        Returns:
            :obj:`~pyrogram.types.Message` | ``None``: On success, the sent message is returned.

        Example:
            .. code-block:: python

                await app.send_live_photo(chat_id, "clip.mp4", "still.jpg")
        """
        if kwargs:
            raise TypeError(f"Got unexpected keyword argument(s): {set(kwargs)}")

        media = await types.InputMediaLivePhoto(
            media=live_photo,
            photo=photo,
            caption=caption,
            parse_mode=parse_mode,
            caption_entities=caption_entities,
            has_spoiler=has_spoiler,
        ).write(
            client=self,
            chat_id=chat_id,
            width=width,
            height=height,
            progress=progress,
            progress_args=progress_args,
        )

        text_params = await utils.parse_text_entities(self, caption, parse_mode, caption_entities)

        r = await self.invoke(
            await as_ephemeral(
                self,
                ephemeral_message_parameters,
                raw.functions.messages.SendMedia(
                    peer=await self.resolve_peer(chat_id),
                    media=media,
                    silent=disable_notification if disable_notification is not None else None,
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
                    invert_media=show_caption_above_media
                    if show_caption_above_media is not None
                    else None,
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
                    reply_markup=await reply_markup.write(self) if reply_markup else None,
                    **text_params,
                ),
            ),
            sleep_threshold=60,
            business_connection_id=business_connection_id,
        )

        for i in r.updates:
            if isinstance(
                i,
                (
                    raw.types.UpdateNewMessage,
                    raw.types.UpdateNewChannelMessage,
                    raw.types.UpdateNewScheduledMessage,
                ),
            ):
                return await types.Message._parse(
                    self,
                    i.message,
                    {i.id: i for i in r.users},
                    {i.id: i for i in r.chats},
                    is_scheduled=isinstance(i, raw.types.UpdateNewScheduledMessage),
                )
