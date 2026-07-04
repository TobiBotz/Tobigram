from typing import Union, List, Optional

import pyrogram
from pyrogram import raw, enums
from pyrogram import types
from pyrogram import utils


class EditMessageText:
    async def edit_message_text(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        message_id: int,
        text: str,
        parse_mode: Optional["enums.ParseMode"] = None,
        entities: List["types.MessageEntity"] = None,
        link_preview_options: Optional["types.LinkPreviewOptions"] = None,
        show_caption_above_media: bool = None,
        disable_web_page_preview: bool = None,
        business_connection_id: str = None,
        rich_text: str = None,
        rich_text_parse_mode: "enums.ParseMode" = enums.ParseMode.MARKDOWN,
        reply_markup: "types.InlineKeyboardMarkup" = None,
    ) -> "types.Message":
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

        invert_media = invert_media or show_caption_above_media or None

        if rich_text:
            if rich_text_parse_mode == enums.ParseMode.HTML:
                rich_msg = raw.types.InputRichMessageHTML(html=rich_text)
            else:
                rich_msg = raw.types.InputRichMessageMarkdown(markdown=rich_text)
            text_params = {"message": "", "rich_message": rich_msg}
        else:
            text_params = await utils.parse_text_entities(self, text, parse_mode, entities)

        r = await self.invoke(
            raw.functions.messages.EditMessage(
                peer=await self.resolve_peer(chat_id),
                id=message_id,
                no_webpage=no_webpage,
                invert_media=invert_media,
                reply_markup=await reply_markup.write(self) if reply_markup else None,
                **text_params
            )
        )

        for i in r.updates:
            if isinstance(i, (raw.types.UpdateEditMessage, raw.types.UpdateEditChannelMessage)):
                return await types.Message._parse(
                    self, i.message,
                    {i.id: i for i in r.users},
                    {i.id: i for i in r.chats}
                )
