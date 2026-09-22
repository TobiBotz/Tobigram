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


class GetBoostsList:
    async def get_boosts_list(
        self: pyrogram.Client,
        chat_id: int | str,
        offset: str = "",
        limit: int = 10,
        gifts: bool | None = None,
    ) -> raw.base.premium.BoostsList:
        """Obtains info about the boosts that were applied to a certain channel or supergroup (admins only).

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target channel or supergroup.

            offset (``str``, *optional*):
                Offset for pagination. Defaults to empty string.

            limit (``int``, *optional*):
                Maximum number of results to return. Defaults to 10.

            gifts (``bool``, *optional*):
                Whether to return only info about boosts received from gift codes and giveaways.

        Returns:
            :obj:`~pyrogram.raw.base.premium.BoostsList`: The boosts list.

        Example:
            .. code-block:: python

                boosts = await app.get_boosts_list(chat_id)
        """
        return await self.invoke(
            raw.functions.premium.GetBoostsList(
                peer=await self.resolve_peer(chat_id),
                offset=offset,
                limit=limit,
                gifts=gifts,
            )
        )
