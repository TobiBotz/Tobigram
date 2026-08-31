from datetime import datetime
from typing import List, Union, Optional

import pyrogram
from pyrogram import raw, utils, enums
from pyrogram import types

from ..ephemeral.as_ephemeral import as_ephemeral


class SendRichMessage:
    async def send_rich_message(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        rich_text: Union[str, "types.InputRichMessage"],
        parse_mode: Optional["enums.ParseMode"] = None,
        media: Optional[List["types.InputRichMessageMedia"]] = None,
        disable_web_page_preview: Optional[bool] = None,
        disable_notification: Optional[bool] = None,
        effect_id: Optional[int] = None,
        protect_content: Optional[bool] = None,
        reply_parameters: Optional["types.ReplyParameters"] = None,
        reply_markup: Optional[Union[
            "types.InlineKeyboardMarkup",
            "types.ReplyKeyboardMarkup",
            "types.ReplyKeyboardRemove",
            "types.ForceReply"
        ]] = None,
        message_thread_id: Optional[int] = None,
        schedule_date: Optional[datetime] = None,
        background: Optional[bool] = None,
        clear_draft: Optional[bool] = None,
        update_stickersets_order: Optional[bool] = None,
        send_as: Optional[Union[int, str]] = None,
        quick_reply_shortcut: Optional[int] = None,
        repeat_period: Optional[int] = None,
        allow_paid_broadcast: Optional[bool] = None,
        paid_message_star_count: Optional[int] = None,
        direct_messages_topic_id: Optional[int] = None,
        suggested_post_parameters: Optional["types.SuggestedPostParameters"] = None,
        show_caption_above_media: Optional[bool] = None,
        business_connection_id: Optional[str] = None,
        ephemeral_message_parameters: Optional["types.EphemeralMessageParameters"] = None,
    ) -> "types.Message":
        """Send a rich formatted message.

        .. include:: /_includes/usable-by/bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            rich_text (``str`` | :obj:`~pyrogram.types.InputRichMessage`):
                Rich text (Markdown or HTML) to render a styled message, or a whole
                :obj:`~pyrogram.types.InputRichMessage` describing it.
                See `rich message formatting options <https://core.telegram.org/bots/api#rich-message-formatting-options>`__ for details.

            parse_mode (:obj:`~pyrogram.enums.ParseMode`, *optional*):
                By default, texts are parsed as Markdown.
                Pass :obj:`~pyrogram.enums.ParseMode.HTML` to parse them as HTML instead;
                the two styles are exclusive and cannot be combined.
                Ignored when *rich_text* is an :obj:`~pyrogram.types.InputRichMessage`.

            media (List of :obj:`~pyrogram.types.InputRichMessageMedia`, *optional*):
                Media the text refers to through ``tg://photo?id=``, ``tg://video?id=``
                or ``tg://audio?id=`` links.
                Ignored when *rich_text* is an :obj:`~pyrogram.types.InputRichMessage`.

            disable_web_page_preview (``bool``, *optional*):
                Disables link previews for links in this message.

            disable_notification (``bool``, *optional*):
                Sends the message silently. Users will receive a notification with no sound.

            effect_id (``int``, *optional*):
                Unique identifier of the effect to apply to the message.

            protect_content (``bool``, *optional*):
                Pass True to protect the message content from being forwarded.

            reply_parameters (:obj:`~pyrogram.types.ReplyParameters`, *optional*):
                Description of the reply-to message.

            reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardRemove` | :obj:`~pyrogram.types.ForceReply`, *optional*):
                Additional interface options.

            message_thread_id (``int``, *optional*):
                Unique identifier for a message thread in a forum topic.

            schedule_date (:py:obj:`~datetime.datetime`, *optional*):
                Date when the message will be automatically sent.

            business_connection_id (``str``, *optional*):
                Unique identifier of the business connection.

            background (``bool``, *optional*):
                Send the message in background.

            clear_draft (``bool``, *optional*):
                Clear the draft of the chat.

            update_stickersets_order (``bool``, *optional*):
                Move the sticker set to the top of the list.

            send_as (``int`` | ``str``, *optional*):
                Unique identifier (int) or username (str) of the chat or channel to send the message as.

            quick_reply_shortcut (``int``, *optional*):
                Unique identifier of the quick reply shortcut to use.

            repeat_period (``int``, *optional*):
                Period in seconds for the message to be sent repeatedly.

            allow_paid_broadcast (``bool``, *optional*):
                Pay to skip the broadcast flood limit.

            paid_message_star_count (``int``, *optional*):
                The number of Telegram Stars the user agreed to pay to send the message.

            direct_messages_topic_id (``int``, *optional*):
                Unique identifier of the direct messages topic.

            suggested_post_parameters (:obj:`~pyrogram.types.SuggestedPostParameters`, *optional*):
                Parameters of the suggested post.

            show_caption_above_media (``bool``, *optional*):
                Pass True, if the caption must be shown above the message media.

            ephemeral_message_parameters (:obj:`~pyrogram.types.EphemeralMessageParameters`, *optional*):
                Send the message as an ephemeral message, visible only to the user it
                names and absent from the chat's history, rather than as an ordinary one.
                The ephemeral RPC has no field for *silent*, *background*, *clear_draft*,
                *schedule_date*, *repeat_period*, *send_as*, *effect_id*,
                *quick_reply_shortcut*, *allow_paid_broadcast*,
                *paid_message_star_count*, *suggested_post_parameters* or
                *update_stickersets_order*; any of those that is set is logged and
                dropped.
        Returns:
            :obj:`~pyrogram.types.Message`: On success, the sent rich message is returned.

        Example:
            .. code-block:: python

                # Send a rich formatted message
                await app.send_rich_message(chat_id, "**Hello** __world__!")
        """
        if isinstance(rich_text, types.InputRichMessage):
            rich_message = rich_text.write()
        else:
            parse_mode = parse_mode or self.parse_mode
            files = types.InputRichMessage(
                html="_", media=media
            ).write_files() if media else None

            if parse_mode == enums.ParseMode.HTML:
                rich_message = raw.types.InputRichMessageHTML(
                    html=rich_text,
                    files=files,
                )
            else:
                rich_message = raw.types.InputRichMessageMarkdown(
                    markdown=rich_text,
                    files=files,
                )

        r = await self.invoke(
            await as_ephemeral(self, ephemeral_message_parameters, raw.functions.messages.SendMessage(
                peer=await self.resolve_peer(chat_id),
                message="",
                random_id=self.rnd_id(),
                no_webpage=disable_web_page_preview if disable_web_page_preview is not None else None,
                silent=disable_notification if disable_notification is not None else None,
                noforwards=protect_content,
                effect=effect_id,
                reply_to=await utils.get_reply_to(
                    self,
                    reply_parameters,
                    message_thread_id,
                    direct_messages_topic_id=direct_messages_topic_id
                ),
                reply_markup=await reply_markup.write(self) if reply_markup else None,
                schedule_date=utils.datetime_to_timestamp(schedule_date),
                rich_message=rich_message,
                background=background,
                clear_draft=clear_draft,
                update_stickersets_order=update_stickersets_order,
                send_as=await self.resolve_peer(send_as) if send_as is not None else None,
                quick_reply_shortcut=raw.types.InputQuickReplyShortcutId(shortcut_id=quick_reply_shortcut) if quick_reply_shortcut is not None else None,
                schedule_repeat_period=repeat_period,
                allow_paid_floodskip=allow_paid_broadcast,
                allow_paid_stars=paid_message_star_count if paid_message_star_count is not None else None,
                suggested_post=suggested_post_parameters.write() if suggested_post_parameters else None,
                invert_media=show_caption_above_media,
            )),
            sleep_threshold=60,
            business_connection_id=business_connection_id,
        )

        for i in r.updates:
            if isinstance(i, (raw.types.UpdateNewMessage,
                              raw.types.UpdateNewChannelMessage,
                              raw.types.UpdateNewScheduledMessage,
                              raw.types.UpdateNewEphemeralMessage)):
                return await types.Message._parse(
                    self, i.message,
                    {i.id: i for i in r.users},
                    {i.id: i for i in r.chats},
                    is_scheduled=isinstance(i, raw.types.UpdateNewScheduledMessage)
                )
