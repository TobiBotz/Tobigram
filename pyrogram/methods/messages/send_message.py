from datetime import datetime
from typing import Union, List, Optional

import pyrogram
from pyrogram import raw, utils, enums
from pyrogram import types


class SendMessage:
    async def send_message(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        text: str = "",
        parse_mode: Optional["enums.ParseMode"] = None,
        entities: List["types.MessageEntity"] = None,
        link_preview_options: Optional["types.LinkPreviewOptions"] = None,
        disable_notification: bool = None,
        message_thread_id: int = None,
        direct_messages_topic_id: int = None,
        effect_id: int = None,
        show_caption_above_media: bool = None,
        reply_parameters: Optional["types.ReplyParameters"] = None,
        schedule_date: datetime = None,
        repeat_period: int = None,
        protect_content: bool = None,
        business_connection_id: str = None,
        allow_paid_broadcast: bool = None,
        paid_message_star_count: int = None,
        suggested_post_parameters: Optional["types.SuggestedPostParameters"] = None,
        reply_markup: Union[
            "types.InlineKeyboardMarkup",
            "types.ReplyKeyboardMarkup",
            "types.ReplyKeyboardRemove",
            "types.ForceReply"
        ] = None,
        rich_text: str = None,
        rich_text_parse_mode: str = "markdown",
        disable_web_page_preview: bool = None,
        reply_to_message_id: int = None,
        reply_to_chat_id: Union[int, str] = None,
        quote_text: str = None,
        quote_entities: List["types.MessageEntity"] = None,
    ) -> "types.Message":
        if rich_text:
            if rich_text_parse_mode == "html":
                rich_message = raw.types.InputRichMessageHTML(
                    html=rich_text,
                    noautolink=disable_web_page_preview or None,
                )
            else:
                rich_message = raw.types.InputRichMessageMarkdown(
                    markdown=rich_text,
                    noautolink=disable_web_page_preview or None,
                )
            r = await self.invoke(
                raw.functions.messages.SendMessage(
                    peer=await self.resolve_peer(chat_id),
                    silent=disable_notification or None,
                    reply_to=await utils.get_reply_to(
                        self,
                        reply_parameters,
                        message_thread_id,
                        direct_messages_topic_id=direct_messages_topic_id
                    ),
                    random_id=self.rnd_id(),
                    schedule_date=utils.datetime_to_timestamp(schedule_date),
                    reply_markup=await reply_markup.write(self) if reply_markup else None,
                    message="",
                    rich_message=rich_message,
                    noforwards=protect_content,
                    effect=effect_id,
                    invert_media=show_caption_above_media or None,
                    schedule_repeat_period=repeat_period,
                    allow_paid_floodskip=allow_paid_broadcast,
                    allow_paid_stars=paid_message_star_count,
                    suggested_post=suggested_post_parameters.write() if suggested_post_parameters else None,
                ),
            )
            plain_text = rich_text
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
                no_webpage = disable_web_page_preview or None

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

            plain_text, entities = (await utils.parse_text_entities(self, text, parse_mode, entities)).values()
            r = await self.invoke(
                raw.functions.messages.SendMessage(
                    peer=await self.resolve_peer(chat_id),
                    no_webpage=no_webpage,
                    silent=disable_notification or None,
                    reply_to=await utils.get_reply_to(
                        self,
                        reply_parameters,
                        message_thread_id,
                        direct_messages_topic_id=direct_messages_topic_id
                    ),
                    random_id=self.rnd_id(),
                    schedule_date=utils.datetime_to_timestamp(schedule_date),
                    reply_markup=await reply_markup.write(self) if reply_markup else None,
                    message=plain_text,
                    entities=entities,
                    noforwards=protect_content,
                    effect=effect_id,
                    invert_media=invert_media or show_caption_above_media or None,
                    schedule_repeat_period=repeat_period,
                    allow_paid_floodskip=allow_paid_broadcast,
                    allow_paid_stars=paid_message_star_count,
                    suggested_post=suggested_post_parameters.write() if suggested_post_parameters else None,
                ),
            )

        if isinstance(r, raw.types.UpdateShortSentMessage):
            peer = await self.resolve_peer(chat_id)

            peer_id = (
                peer.user_id
                if isinstance(peer, raw.types.InputPeerUser)
                else -peer.chat_id
            )

            return types.Message(
                id=r.id,
                chat=types.Chat(
                    id=peer_id,
                    type=enums.ChatType.PRIVATE,
                    client=self
                ),
                text=plain_text,
                date=utils.timestamp_to_datetime(r.date),
                outgoing=r.out,
                reply_markup=reply_markup,
                entities=[
                    types.MessageEntity._parse(None, entity, {})
                    for entity in entities
                ] if not rich_text and entities else None,
                client=self
            )

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
