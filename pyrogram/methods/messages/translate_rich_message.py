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


class TranslateRichMessage:
    async def translate_rich_message(
        self: pyrogram.Client,
        chat_id: int | str,
        message_id: int,
        to_lang: str,
        text: raw.base.RichText | None = None,
        tone: str | None = None,
    ) -> raw.base.messages.TranslatedText:
        """Translate a rich message (with formatting) to another language.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            message_id (``int``):
                The message ID to translate.

            to_lang (``str``):
                Target language code (e.g., "en", "ru").

            text (:obj:`~pyrogram.raw.base.RichText`, *optional*):
                Override the message text to translate.

            tone (``str``, *optional*):
                Translation tone/style.

        Returns:
            :obj:`~pyrogram.raw.base.messages.TranslatedText`: The translated text.

        Example:
            .. code-block:: python

                result = await app.translate_rich_message(chat_id, message_id, to_lang="en")
        """
        peer = await self.resolve_peer(chat_id)

        return await self.invoke(
            raw.functions.messages.TranslateRichMessage(
                peer=peer,
                id=message_id,
                text=text,
                to_lang=to_lang,
                tone=tone,
            )
        )
