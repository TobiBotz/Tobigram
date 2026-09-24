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

from collections.abc import AsyncGenerator

import pyrogram
from pyrogram import enums, raw, types


class SearchStickers:
    async def search_stickers(
        self: pyrogram.Client,
        sticker_type: enums.StickerType,
        emojis: list[str],
        query: str = "",
        input_language_codes: list[str] | None = None,
        offset: int = 0,
        limit: int = 0,
    ) -> AsyncGenerator[types.Sticker, None]:
        """Search for stickers from public sticker sets that match any of the given emoji.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            sticker_type (:obj:`~pyrogram.enums.StickerType`):
                Type of the stickers to return.

            emojis (List of ``str``):
                List of emojis to search for.

            query (``str``, *optional*):
                Query to search for. May be empty to search by emoji only.

            input_language_codes (List of ``str``, *optional*):
                List of possible IETF language tags of the user's input language.

            offset (``int``, *optional*):
                The offset from which to return the stickers.

            limit (``int``, *optional*):
                Limits the number of stickers to be retrieved.
                By default, no limit is applied and all stickers are returned.

        Returns:
            ``Generator``: A generator yielding :obj:`~pyrogram.types.Sticker` objects.

        Example:
            .. code-block:: python

                from wzgram import enums

                async for sticker in app.search_stickers(enums.StickerType.REGULAR, ["👍"]):
                    print(sticker)
        """
        current = 0
        total = abs(limit) or (1 << 31) - 1
        limit = min(100, total)

        while True:
            r = await self.invoke(
                raw.functions.messages.SearchStickers(
                    q=query,
                    emoticon="".join(emojis),
                    lang_code=input_language_codes or [],
                    offset=offset,
                    limit=limit,
                    hash=0,
                    emojis=sticker_type == enums.StickerType.CUSTOM_EMOJI,
                )
            )

            stickers = getattr(r, "stickers", [])

            if not stickers:
                return

            for sticker in stickers:
                yield await types.Sticker._parse(
                    self, sticker, {type(a): a for a in sticker.attributes}
                )

                current += 1

                if current >= total:
                    return

            offset = r.next_offset

            if not offset:
                return
