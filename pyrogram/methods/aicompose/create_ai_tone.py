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


class CreateAITone:
    async def create_ai_tone(
        self: pyrogram.Client,
        title: str,
        prompt: str,
        emoji_id: int = 0,
        display_author: bool | None = None,
    ) -> raw.types.AiComposeTone:
        """Create a custom AI writing tone.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            title (``str``):
                The title/name of the writing tone.

            prompt (``str``):
                The prompt instructions describing the writing tone.

            emoji_id (``int``, *optional*):
                Custom emoji document ID representing the tone. Defaults to 0.

            display_author (``bool``, *optional*):
                Whether to display the creator's username.

        Returns:
            :obj:`~pyrogram.raw.types.AiComposeTone`: On success, the created tone is returned.

        Example:
            .. code-block:: python

                tone = await app.create_ai_tone("Pirate", "Speak like a pirate!")
        """
        return await self.invoke(
            raw.functions.aicompose.CreateTone(
                title=title,
                prompt=prompt,
                emoji_id=emoji_id,
                display_author=display_author,
            )
        )
