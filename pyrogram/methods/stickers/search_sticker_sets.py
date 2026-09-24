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
from pyrogram import enums, raw, types


class SearchStickerSets:
    async def search_sticker_sets(
        self: pyrogram.Client, sticker_type: enums.StickerType, query: str
    ) -> list[types.StickerSet]:
        """Search for sticker sets by looking for the query in their title and name.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            sticker_type (:obj:`~pyrogram.enums.StickerType`):
                Type of the sticker sets to return.

            query (``str``):
                Query to search for.

        Returns:
            List of :obj:`~pyrogram.types.StickerSet`: The sticker sets that match the query are returned.

        Example:
            .. code-block:: python

                from wzgram import enums

                await app.search_sticker_sets(enums.StickerType.REGULAR, "cats")
        """
        if sticker_type == enums.StickerType.CUSTOM_EMOJI:
            r = await self.invoke(raw.functions.messages.SearchEmojiStickerSets(q=query, hash=0))
        else:
            r = await self.invoke(raw.functions.messages.SearchStickerSets(q=query, hash=0))

        sticker_sets = types.List()

        for covered in getattr(r, "sets", []):
            sticker_set = await types.StickerSet._parse(self, covered.set)

            if sticker_set.sticker_type == sticker_type:
                sticker_sets.append(sticker_set)

        return sticker_sets
