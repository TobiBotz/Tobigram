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
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator


class GetUserGifts:
    async def get_user_gifts(
        self: pyrogram.Client,
        user_id: int | str,
        exclude_unlimited: bool | None = None,
        exclude_limited_upgradable: bool | None = None,
        exclude_limited_non_upgradable: bool | None = None,
        exclude_unique: bool | None = None,
        sort_by_price: bool | None = None,
        offset: str = "",
        limit: int = 100,
    ) -> AsyncGenerator[types.Gift, None]:
        """Get the gifts owned by a user.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            user_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target user.

            exclude_unlimited (``bool``, *optional*):
                Pass True to exclude non-limited gifts.

            exclude_limited_upgradable (``bool``, *optional*):
                Pass True to exclude limited gifts that can be upgraded to collectible.

            exclude_limited_non_upgradable (``bool``, *optional*):
                Pass True to exclude limited gifts that cannot be upgraded.

            exclude_unique (``bool``, *optional*):
                Pass True to exclude unique/collectible gifts.

            sort_by_price (``bool``, *optional*):
                Pass True to sort gifts by price instead of reception date.

            offset (``str``, *optional*):
                Offset for pagination (use empty string to start from beginning).

            limit (``int``, *optional*):
                Maximum number of results to return. Defaults to 100.

        Returns:
            ``AsyncGenerator``: An async generator yielding :obj:`~pyrogram.types.StarGift` objects.

        Example:
            .. code-block:: python

                # Get all gifts of a user
                async for gift in app.get_user_gifts(user_id):
                    print(gift)
        """
        peer = await self.resolve_peer(user_id)
        current_offset = offset

        while True:
            r = await self.invoke(
                raw.functions.payments.GetSavedStarGifts(
                    peer=peer,
                    offset=current_offset,
                    limit=limit,
                    exclude_unlimited=exclude_unlimited,
                    exclude_unique=exclude_unique,
                    sort_by_value=sort_by_price,
                    exclude_upgradable=exclude_limited_upgradable,
                    exclude_unupgradable=exclude_limited_non_upgradable,
                )
            )

            users = {u.id: u for u in r.users}
            chats = {c.id: c for c in r.chats}

            for gift in r.gifts:
                yield types.StarGift._parse(self, gift, users, chats)

            if not r.next_offset:
                break
            current_offset = r.next_offset
