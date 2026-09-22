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
from pyrogram import raw


class ComposeRichMessageWithAI:
    async def compose_rich_message_with_ai(
        self: pyrogram.Client,
        text: raw.base.InputRichMessage | None = None,
        translate_to_lang: str | None = None,
        tone: str | None = None,
        proofread: bool | None = None,
        emojify: bool | None = None,
    ) -> raw.base.messages.TranslatedText:
        """Use AI to compose, proofread, translate or emojify a rich text message.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            text (:obj:`~pyrogram.raw.base.InputRichMessage`, *optional*):
                The input rich text to process.

            translate_to_lang (``str``, *optional*):
                Target language code to translate to.

            tone (``str``, *optional*):
                The tone/style to use for composition.

            proofread (``bool``, *optional*):
                If True, proofread the text.

            emojify (``bool``, *optional*):
                If True, add relevant emojis.

        Returns:
            :obj:`~pyrogram.raw.base.messages.TranslatedText`: The AI-composed text.

        Example:
            .. code-block:: python

                result = await app.compose_rich_message_with_ai(
                    text=input_rich_msg, proofread=True
                )
        """
        return await self.invoke(
            raw.functions.messages.ComposeRichMessageWithAI(
                text=text,
                translate_to_lang=translate_to_lang,
                tone=tone,
                proofread=proofread,
                emojify=emojify,
            )
        )
