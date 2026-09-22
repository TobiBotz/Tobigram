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
from pyrogram import raw, utils


class GetSavedMusicByID:
    async def get_saved_music_by_id(
        self: pyrogram.Client,
        user_id: int | str,
        documents: list[raw.base.InputDocument],
    ) -> raw.base.users.SavedMusic:
        """Check if the passed songs are still pinned to the user's profile, or refresh their file references.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            user_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target user.

            documents (List of :obj:`~pyrogram.raw.base.InputDocument`):
                List of songs/documents.

        Returns:
            :obj:`~pyrogram.raw.base.users.SavedMusic`: The saved music info.

        Example:
            .. code-block:: python

                music = await app.get_saved_music_by_id(user_id, [doc])
        """
        return await self.invoke(
            raw.functions.users.GetSavedMusicByID(
                id=utils.get_input_user(await self.resolve_peer(user_id)),
                documents=documents,
            )
        )
