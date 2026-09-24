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


class GetCustomEmojiStickers:
    async def get_custom_emoji_stickers(
        self: pyrogram.Client,
        custom_emoji_ids: list[int | str],
    ) -> list[types.Sticker]:
        """Get information about custom emoji stickers by their identifiers.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            custom_emoji_ids (List of ``int`` | ``str``):
                List of custom emoji identifiers.

        Returns:
            List of :obj:`~pyrogram.types.Sticker`: A list of custom emoji stickers.

        Example:
            .. code-block:: python

                stickers = await app.get_custom_emoji_stickers([543210987654321])
        """
        r = await self.invoke(
            raw.functions.messages.GetCustomEmojiDocuments(
                document_id=[int(i) for i in custom_emoji_ids]
            )
        )

        return types.List(
            [
                await types.Sticker._parse(self, doc, {type(a): a for a in doc.attributes})
                for doc in r
                if isinstance(doc, raw.types.Document)
            ]
        )
