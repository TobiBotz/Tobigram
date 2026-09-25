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


class GetArchivedStickers:
    async def get_archived_stickers(
        self: pyrogram.Client,
        masks: bool | None = None,
        emojis: bool | None = None,
        offset_id: int = 0,
        limit: int = 100,
        hash: int = 0,
    ) -> raw.base.messages.ArchivedStickers:
        """Get archived sticker sets.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            masks (``bool``, *optional*):
                If True, return mask sticker sets.

            emojis (``bool``, *optional*):
                If True, return custom emoji sticker sets.

            offset_id (``int``, *optional*):
                Offset sticker set ID for pagination.

            limit (``int``, *optional*):
                Maximum number of results to return. Defaults to 100.

            hash (``int``, *optional*):
                Hash for caching, for more info click `here <https://core.telegram.org/api/offsets#hash-generation>`_.

        Returns:
            :obj:`~pyrogram.raw.base.messages.ArchivedStickers`: The archived stickers object.

        Example:
            .. code-block:: python

                archived = await app.get_archived_stickers()
        """
        return await self.invoke(
            raw.functions.messages.GetArchivedStickers(
                masks=masks,
                emojis=emojis,
                offset_id=offset_id,
                limit=limit,
            )
        )
