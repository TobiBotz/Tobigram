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


class GetSavedMusicIds:
    async def get_saved_music_ids(
        self: pyrogram.Client,
        hash: int = 0,
    ) -> raw.base.account.SavedMusicIds:
        """Fetch the full list of only the IDs of songs currently added to the profile.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            hash (``int``, *optional*):
                Hash generated from the previously returned list of IDs, defaults to 0.

        Returns:
            :obj:`~pyrogram.raw.base.account.SavedMusicIds`: On success, saved music IDs are returned.
        """
        return await self.invoke(
            raw.functions.account.GetSavedMusicIds(
                hash=hash,
            )
        )
