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
from pyrogram import raw, types


class EmojifyTextWithAI:
    async def emojify_text_with_ai(
        self: pyrogram.Client,
        text: str | types.FormattedText,
    ) -> types.FormattedText:
        """Adds emojis to text using an AI model.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            text (``str`` | :obj:`~pyrogram.types.FormattedText`):
                The original text.

        Returns:
            :obj:`~pyrogram.types.FormattedText`: On success, information about the emojified text is returned.

        Example:
            .. code-block:: python

                result = await app.emojify_text_with_ai("Good morning my friend, have a wonderful day!")
                print(result.text)
        """
        if isinstance(text, str):
            text = types.FormattedText(text=text)

        r = await self.invoke(
            raw.functions.messages.ComposeMessageWithAI(
                text=await text.write(self),
                emojify=True,
            )
        )

        return types.FormattedText._parse(self, r.result_text)
