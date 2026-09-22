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


class GetSavedStarGift:
    async def get_saved_star_gift(
        self: pyrogram.Client,
        stargift: raw.base.InputSavedStarGift | list[raw.base.InputSavedStarGift],
    ) -> raw.types.payments.SavedStarGifts:
        """Get one or more saved star gifts by their input identifiers.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            stargift (:obj:`~pyrogram.raw.base.InputSavedStarGift` | List of :obj:`~pyrogram.raw.base.InputSavedStarGift`):
                Input saved star gift identifier(s).

        Returns:
            :obj:`~pyrogram.raw.types.payments.SavedStarGifts`: On success, saved star gifts are returned.

        Example:
            .. code-block:: python

                gifts = await app.get_saved_star_gift(stargift)
        """
        gifts = [stargift] if not isinstance(stargift, list) else stargift

        return await self.invoke(
            raw.functions.payments.GetSavedStarGift(
                stargift=gifts,
            )
        )
