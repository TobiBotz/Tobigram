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


class UpdateAITone:
    async def update_ai_tone(
        self: pyrogram.Client,
        tone: raw.base.InputAiComposeTone,
        title: str | None = None,
        prompt: str | None = None,
        emoji_id: int | None = None,
        display_author: bool | None = None,
    ) -> raw.types.AiComposeTone:
        """Update an existing custom AI writing tone.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            tone (:obj:`~pyrogram.raw.base.InputAiComposeTone`):
                Input AI tone identifier.

            title (``str``, *optional*):
                Updated title/name of the tone.

            prompt (``str``, *optional*):
                Updated prompt instructions.

            emoji_id (``int``, *optional*):
                Updated custom emoji document ID.

            display_author (``bool``, *optional*):
                Whether to display the creator's username.

        Returns:
            :obj:`~pyrogram.raw.types.AiComposeTone`: On success, updated tone is returned.

        Example:
            .. code-block:: python

                updated = await app.update_ai_tone(tone, title="New Pirate")
        """
        return await self.invoke(
            raw.functions.aicompose.UpdateTone(
                tone=tone,
                title=title,
                prompt=prompt,
                emoji_id=emoji_id,
                display_author=display_author,
            )
        )
