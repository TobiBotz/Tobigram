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


class SaveAITone:
    async def save_ai_tone(
        self: pyrogram.Client,
        tone: raw.base.InputAiComposeTone,
        unsave: bool = False,
    ) -> bool:
        """Install or uninstall an AI composer tone, adding it to or removing it from the list of saved tones.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            tone (:obj:`~pyrogram.raw.base.InputAiComposeTone`):
                The tone to save or unsave.

            unsave (``bool``, *optional*):
                If ``False`` (default), installs (saves) the tone; if ``True``, uninstalls (unsaves) it.

        Returns:
            ``bool``: On success, True is returned.

        Example:
            .. code-block:: python

                # Save tone
                await app.save_ai_tone(tone)

                # Unsave tone
                await app.save_ai_tone(tone, unsave=True)
        """
        return await self.invoke(
            raw.functions.aicompose.SaveTone(
                tone=tone,
                unsave=unsave,
            )
        )
