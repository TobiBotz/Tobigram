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
from pyrogram import raw, types, utils


class TranslateRichMessage:
    async def translate_rich_message(
        self: pyrogram.Client,
        chat_id: int | str | None = None,
        message_id: int | list[int] | None = None,
        to_lang: str = "en",
        text: (
            raw.base.InputRichMessage
            | list[raw.base.InputRichMessage]
            | str
            | types.InputRichMessage
            | types.RichMessage
            | None
        ) = None,
        tone: str | None = None,
    ) -> types.RichMessage | list[types.RichMessage]:
        """Translate a rich message (with formatting) to another language.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``, *optional*):
                Unique identifier (int) or username (str) of the target chat.

            message_id (``int`` | List of ``int``, *optional*):
                The message ID(s) to translate.

            to_lang (``str``):
                Target language code (e.g., "en", "ru").

            text (:obj:`~pyrogram.raw.base.InputRichMessage` | List of :obj:`~pyrogram.raw.base.InputRichMessage` | ``str`` | :obj:`~pyrogram.types.InputRichMessage`, *optional*):
                The rich message content to translate.

            tone (``str``, *optional*):
                Translation tone/style.

        Returns:
            :obj:`~pyrogram.types.RichMessage` | List of :obj:`~pyrogram.types.RichMessage`: The translated rich message(s).

        Example:
            .. code-block:: python

                result = await app.translate_rich_message(chat_id, message_id, to_lang="en")
        """
        peer = await self.resolve_peer(chat_id) if chat_id is not None else None
        is_single = isinstance(message_id, int) or (text is not None and not isinstance(text, list))

        if isinstance(message_id, int):
            message_id = [message_id]

        if text is not None:
            if not isinstance(text, list):
                if isinstance(text, (str, types.InputRichMessage, types.RichMessage)):
                    text = [await utils.build_input_rich_message(self, text, chat_id=chat_id)]
                elif isinstance(text, raw.base.InputRichMessage):
                    text = [text]

        r = await self.invoke(
            raw.functions.messages.TranslateRichMessage(
                peer=peer,
                id=message_id,
                text=text,
                to_lang=to_lang,
                tone=tone,
            )
        )

        if isinstance(r, raw.types.messages.TranslatedRichMessage):
            parsed = types.List([await types.RichMessage._parse(self, msg) for msg in r.result])
            if is_single and len(parsed) == 1:
                return parsed[0]
            return parsed

        return r
