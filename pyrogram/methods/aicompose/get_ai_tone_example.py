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


class GetAIToneExample:
    async def get_ai_tone_example(
        self: pyrogram.Client,
        tone: raw.base.InputAiComposeTone,
        example_number: int = 1,
    ) -> raw.types.AiComposeToneExample:
        """Get an example generated text for a specific AI writing tone.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            tone (:obj:`~pyrogram.raw.base.InputAiComposeTone`):
                Input AI tone identifier.

            example_number (``int``, *optional*):
                The index/number of the example. Defaults to 1.

        Returns:
            :obj:`~pyrogram.raw.types.AiComposeToneExample`: Generated tone example.

        Example:
            .. code-block:: python

                example = await app.get_ai_tone_example(tone, 1)
        """
        return await self.invoke(
            raw.functions.aicompose.GetToneExample(
                tone=tone,
                num=example_number,
            )
        )
