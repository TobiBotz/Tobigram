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


class RephraseTextWithAI:
    async def rephrase_text_with_ai(
        self: pyrogram.Client,
        text: str | types.FormattedText,
        tone: str | raw.base.InputAiComposeTone = "formal",
    ) -> types.FormattedText:
        """Rephrases text using an AI model tone.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            text (``str`` | :obj:`~pyrogram.types.FormattedText`):
                The original text.

            tone (``str`` | :obj:`~pyrogram.raw.base.InputAiComposeTone`, *optional*):
                The desired AI composition tone (e.g. "formal", "casual", "poetic").
                Defaults to "formal".

        Returns:
            :obj:`~pyrogram.types.FormattedText`: On success, information about the rephrased text is returned.

        Example:
            .. code-block:: python

                result = await app.rephrase_text_with_ai("hey guys what's up", tone="formal")
                print(result.text)
        """
        if isinstance(text, str):
            text = types.FormattedText(text=text)

        raw_tone = raw.types.InputAiComposeToneDefault(tone=tone) if isinstance(tone, str) else tone

        r = await self.invoke(
            raw.functions.messages.ComposeMessageWithAI(
                text=await text.write(self),
                tone=raw_tone,
            )
        )

        return types.FormattedText._parse(self, r.result_text)
