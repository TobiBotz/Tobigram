from __future__ import annotations

from datetime import datetime

import pyrogram
from pyrogram import enums, raw, types, utils

from ..ephemeral.as_ephemeral import as_ephemeral


class SendMessage:
    async def send_message(
        self: pyrogram.Client,
        chat_id: int | str,
        text: str = "",
        parse_mode: enums.ParseMode | None = None,
        entities: list[types.MessageEntity] | None = None,
        link_preview_options: types.LinkPreviewOptions | None = None,
        disable_notification: bool | None = None,
        message_thread_id: int | None = None,
        direct_messages_topic_id: int | None = None,
        effect_id: int | None = None,
        show_caption_above_media: bool | None = None,
        reply_parameters: types.ReplyParameters | None = None,
        schedule_date: datetime | None = None,
        repeat_period: int | None = None,
        protect_content: bool | None = None,
        business_connection_id: str | None = None,
        allow_paid_broadcast: bool | None = None,
        paid_message_star_count: int | None = None,
        suggested_post_parameters: types.SuggestedPostParameters | None = None,
        reply_markup: types.InlineKeyboardMarkup
        | types.ReplyKeyboardMarkup
        | types.ReplyKeyboardRemove
        | types.ForceReply
        | None = None,
        rich_text: str | types.InputRichMessage | None = None,
        rich_text_parse_mode: enums.ParseMode = enums.ParseMode.MARKDOWN,
        rich_text_media: list[types.InputRichMessageMedia] | None = None,
        disable_web_page_preview: bool | None = None,
        reply_to_message_id: int | None = None,
        reply_to_chat_id: int | str | None = None,
        quote_text: str | None = None,
        quote_entities: list[types.MessageEntity] | None = None,
        background: bool | None = None,
        clear_draft: bool | None = None,
        update_stickersets_order: bool | None = None,
        send_as: int | str | None = None,
        quick_reply_shortcut: int | None = None,
        ephemeral_message_parameters: types.EphemeralMessageParameters | None = None,
    ) -> types.Message:
        """Send text messages.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            text (``str``, *optional*):
                Text of the message to be sent. If ``rich_text`` is provided, this is ignored.

            parse_mode (:obj:`~pyrogram.enums.ParseMode`, *optional*):
                By default, texts are parsed using both Markdown and HTML styles.
                You can combine both syntaxes.

            entities (List of :obj:`~pyrogram.types.MessageEntity`, *optional*):
                List of special entities that appear in message text, which can be specified
                instead of *parse_mode*.

            link_preview_options (:obj:`~pyrogram.types.LinkPreviewOptions`, *optional*):
                Link preview generation options for the message.

            disable_notification (``bool``, *optional*):
                Sends the message silently. Users will receive a notification with no sound.

            message_thread_id (``int``, *optional*):
                Unique identifier for a message thread in a forum topic.

            direct_messages_topic_id (``int``, *optional*):
                Topic ID for direct messages in channel admin logs.

            effect_id (``int``, *optional*):
                Unique identifier of the effect to apply to the message.

            show_caption_above_media (``bool``, *optional*):
                Pass True to show the caption above the media.

            reply_parameters (:obj:`~pyrogram.types.ReplyParameters`, *optional*):
                Description of the reply-to message.

            schedule_date (:py:obj:`~datetime.datetime`, *optional*):
                Date when the message will be automatically sent.

            repeat_period (``int``, *optional*):
                Period in seconds after which the message will be automatically repeated.

            protect_content (``bool``, *optional*):
                Pass True to protect the message content from being forwarded.

            business_connection_id (``str``, *optional*):
                Unique identifier of the business connection.

            allow_paid_broadcast (``bool``, *optional*):
                Pass True to allow sending paid broadcast messages.

            paid_message_star_count (``int``, *optional*):
                Number of Telegram Stars to require for access to the paid message.

            suggested_post_parameters (:obj:`~pyrogram.types.SuggestedPostParameters`, *optional*):
                Parameters for creating a suggested channel post.

            reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardRemove` | :obj:`~pyrogram.types.ForceReply`, *optional*):
                Additional interface options. An object for an inline keyboard, custom reply keyboard,
                instructions to remove reply keyboard or to force a reply from the user.

            rich_text (``str`` | :obj:`~pyrogram.types.InputRichMessage`, *optional*):
                Rich text (Markdown or HTML) to render a styled message, or a whole
                :obj:`~pyrogram.types.InputRichMessage` describing it. Overrides ``text``.

            rich_text_parse_mode (:obj:`~pyrogram.enums.ParseMode`, *optional*):
                Parse mode for ``rich_text``. Defaults to Markdown.
                Ignored when ``rich_text`` is an :obj:`~pyrogram.types.InputRichMessage`.

            rich_text_media (List of :obj:`~pyrogram.types.InputRichMessageMedia`, *optional*):
                Media ``rich_text`` refers to through ``tg://photo?id=``,
                ``tg://video?id=`` or ``tg://audio?id=`` links.
                Ignored when ``rich_text`` is an :obj:`~pyrogram.types.InputRichMessage`.

            disable_web_page_preview (``bool``, *optional*):
                Disables link previews for links in this message.

            reply_to_message_id (``int``, *optional*):
                Message identifier to reply to. Deprecated, use ``reply_parameters`` instead.

            reply_to_chat_id (``int`` | ``str``, *optional*):
                Unique identifier for the origin chat of the replied message.

            quote_text (``str``, *optional*):
                Text to quote from the replied message.

            quote_entities (List of :obj:`~pyrogram.types.MessageEntity`, *optional*):
                Entities for the quoted text.

            background (``bool``, *optional*):
                Pass True to send the message as a background message.

            clear_draft (``bool``, *optional*):
                Pass True to clear the draft in the chat.

            update_stickersets_order (``bool``, *optional*):
                Pass True to update the stickersets order.

            send_as (``int`` | ``str``, *optional*):
                Unique identifier of the chat or user to send the message on behalf of.

            quick_reply_shortcut (``int``, *optional*):
                Shortcut ID for quick reply.

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
            :obj:`~pyrogram.types.Message`: On success, the sent message is returned.

        Example:
            .. code-block:: python

                # Send a simple text message

                await app.send_message("me", "Hello from pyrogram!")

                # Send a message with a link preview
                await app.send_message("me", "Check this out: https://example.com")
        """
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

        if rich_text is not None:
            rich_message = await utils.build_input_rich_message(
                self, rich_text, rich_text_parse_mode, rich_text_media, chat_id
            )
            r = await self.invoke(
                await as_ephemeral(
                    self,
                    ephemeral_message_parameters,
                    raw.functions.messages.SendMessage(
                        peer=await self.resolve_peer(chat_id),
                        silent=disable_notification if disable_notification is not None else None,
                        no_webpage=disable_web_page_preview
                        if disable_web_page_preview is not None
                        else None,
                        reply_to=await utils.get_reply_to(
                            self,
                            reply_parameters,
                            message_thread_id,
                            direct_messages_topic_id=direct_messages_topic_id,
                        ),
                        random_id=self.rnd_id(),
                        schedule_date=utils.datetime_to_timestamp(schedule_date),
                        reply_markup=await reply_markup.write(self) if reply_markup else None,
                        message="",
                        rich_message=rich_message,
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
                        background=background,
                        clear_draft=clear_draft,
                        update_stickersets_order=update_stickersets_order,
                        send_as=await self.resolve_peer(send_as) if send_as is not None else None,
                        quick_reply_shortcut=raw.types.InputQuickReplyShortcutId(
                            shortcut_id=quick_reply_shortcut
                        )
                        if quick_reply_shortcut is not None
                        else None,
                    ),
                ),
                sleep_threshold=60,
                business_connection_id=business_connection_id,
            )
            plain_text = (
                rich_text.html or rich_text.markdown or ""
                if isinstance(rich_text, types.InputRichMessage)
                else rich_text
            )
        else:
            if link_preview_options is None:
                link_preview_options = self.link_preview_options

            no_webpage = None
            invert_media = None

            if link_preview_options is not None:
                if link_preview_options.is_disabled:
                    no_webpage = True

                if link_preview_options.show_above_text:
                    invert_media = True

            if disable_web_page_preview is not None:
                no_webpage = (
                    disable_web_page_preview if disable_web_page_preview is not None else None
                )

            plain_text, entities = (
                await utils.parse_text_entities(self, text, parse_mode, entities)
            ).values()
            request = {
                "peer": await self.resolve_peer(chat_id),
                "silent": disable_notification if disable_notification is not None else None,
                "reply_to": await utils.get_reply_to(
                    self,
                    reply_parameters,
                    message_thread_id,
                    direct_messages_topic_id=direct_messages_topic_id,
                ),
                "random_id": self.rnd_id(),
                "schedule_date": utils.datetime_to_timestamp(schedule_date),
                "reply_markup": await reply_markup.write(self) if reply_markup else None,
                "message": plain_text,
                "entities": entities,
                "noforwards": protect_content,
                "effect": effect_id,
                "invert_media": invert_media
                if invert_media is not None
                else (show_caption_above_media if show_caption_above_media is not None else None),
                "schedule_repeat_period": repeat_period,
                "allow_paid_floodskip": allow_paid_broadcast
                if allow_paid_broadcast is not None
                else None,
                "allow_paid_stars": paid_message_star_count
                if paid_message_star_count is not None
                else None,
                "suggested_post": suggested_post_parameters.write()
                if suggested_post_parameters
                else None,
                "background": background,
                "clear_draft": clear_draft,
                "update_stickersets_order": update_stickersets_order,
                "send_as": await self.resolve_peer(send_as) if send_as is not None else None,
                "quick_reply_shortcut": raw.types.InputQuickReplyShortcutId(
                    shortcut_id=quick_reply_shortcut
                )
                if quick_reply_shortcut is not None
                else None,
            }

            if link_preview_options is not None and link_preview_options.url:
                request = await as_ephemeral(
                    self,
                    ephemeral_message_parameters,
                    raw.functions.messages.SendMedia(
                        media=raw.types.InputMediaWebPage(
                            url=link_preview_options.url,
                            force_large_media=link_preview_options.prefer_large_media,
                            force_small_media=link_preview_options.prefer_small_media,
                            optional=True,
                        ),
                        **request,
                    ),
                )
            else:
                request = await as_ephemeral(
                    self,
                    ephemeral_message_parameters,
                    raw.functions.messages.SendMessage(no_webpage=no_webpage, **request),
                )

            r = await self.invoke(
                request, sleep_threshold=60, business_connection_id=business_connection_id
            )

        if isinstance(r, raw.types.UpdateShortSentMessage):
            peer = await self.resolve_peer(chat_id)

            peer_id = (
                peer.user_id
                if isinstance(peer, (raw.types.InputPeerUser, raw.types.InputPeerUserFromMessage))
                else -peer.chat_id
            )

            return types.Message(
                id=r.id,
                chat=types.Chat(id=peer_id, type=enums.ChatType.PRIVATE, client=self),
                text=plain_text,
                date=utils.timestamp_to_datetime(r.date),
                outgoing=r.out,
                reply_markup=reply_markup,
                entities=[types.MessageEntity._parse(None, entity, {}) for entity in entities]
                if not rich_text and entities
                else None,
                client=self,
            )

        for i in r.updates:
            if isinstance(
                i,
                (
                    raw.types.UpdateNewMessage,
                    raw.types.UpdateNewChannelMessage,
                    raw.types.UpdateNewScheduledMessage,
                    raw.types.UpdateNewEphemeralMessage,
                    raw.types.UpdateBotNewBusinessMessage,
                ),
            ):
                return await types.Message._parse(
                    self,
                    i.message,
                    {i.id: i for i in r.users},
                    {i.id: i for i in r.chats},
                    is_scheduled=isinstance(i, raw.types.UpdateNewScheduledMessage),
                )
