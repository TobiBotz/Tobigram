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
from pyrogram import enums, raw, types, utils

from .inline_session import invoke_inline


class EditInlineText:
    async def edit_inline_text(
        self: pyrogram.Client,
        inline_message_id: str,
        text: str,
        parse_mode: enums.ParseMode | None = None,
        entities: list[types.MessageEntity] | None = None,
        link_preview_options: types.LinkPreviewOptions | None = None,
        disable_web_page_preview: bool | None = None,
        show_caption_above_media: bool | None = None,
        reply_markup: types.InlineKeyboardMarkup | None = None,
        business_connection_id: str | None = None,
    ) -> bool:
        """Edit the text of inline messages.

        .. include:: /_includes/usable-by/bots.rst

        Parameters:
            inline_message_id (``str``):
                Identifier of the inline message.

            text (``str``):
                New text of the message.

            parse_mode (:obj:`~pyrogram.enums.ParseMode`, *optional*):
                By default, texts are parsed using both Markdown and HTML styles.
                You can combine both syntaxes together.

            entities (List of :obj:`~pyrogram.types.MessageEntity`, *optional*):
                List of special entities that appear in the new text, which can be specified instead of
                *parse_mode*.

            link_preview_options (:obj:`~pyrogram.types.LinkPreviewOptions`, *optional*):
                Link preview generation options for the message.

            disable_web_page_preview (``bool``, *optional*):
                Disables link previews for links in this message.

            reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup`, *optional*):
                An InlineKeyboardMarkup object.

            show_caption_above_media (``bool``, *optional*):
                Pass True, if the caption must be shown above the message media.

            business_connection_id (``str``, *optional*):
                Unique identifier of the business connection.

        Returns:
            ``bool``: On success, True is returned.

        Example:
            .. code-block:: python

                # Bots only

                # Simple edit text
                await app.edit_inline_text(inline_message_id, "new text")

                # Take the same text message, remove the web page preview only
                await app.edit_inline_text(
                    inline_message_id, message.text,
                    disable_web_page_preview=True)
        """

        unpacked = utils.unpack_inline_message_id(inline_message_id)
        dc_id = unpacked.dc_id

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
            no_webpage = disable_web_page_preview

        if invert_media is None and show_caption_above_media is not None:
            invert_media = show_caption_above_media

        return await invoke_inline(
            self,
            dc_id,
            raw.functions.messages.EditInlineBotMessage(
                id=unpacked,
                no_webpage=no_webpage,
                invert_media=invert_media,
                media=raw.types.InputMediaWebPage(
                    url=link_preview_options.url,
                    force_large_media=link_preview_options.prefer_large_media,
                    force_small_media=link_preview_options.prefer_small_media,
                    optional=True,
                )
                if link_preview_options is not None and link_preview_options.url
                else None,
                reply_markup=await reply_markup.write(self) if reply_markup else None,
                **await utils.parse_text_entities(self, text, parse_mode, entities),
            ),
            business_connection_id,
        )
