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


class GetAITone:
    async def get_ai_tone(
        self: pyrogram.Client,
        tone: raw.base.InputAiComposeTone,
    ) -> raw.types.aicompose.Tones:
        """Get details about a specific AI writing tone.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            tone (:obj:`~pyrogram.raw.base.InputAiComposeTone`):
                Input AI tone identifier.

        Returns:
            :obj:`~pyrogram.raw.types.aicompose.Tones`: The tone details.

        Example:
            .. code-block:: python

                tone_info = await app.get_ai_tone(tone)
        """
        return await self.invoke(
            raw.functions.aicompose.GetTone(
                tone=tone,
            )
        )
