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


class GetUserBoosts:
    async def get_user_boosts(
        self: pyrogram.Client,
        chat_id: int | str,
        user_id: int | str,
    ) -> raw.base.premium.BoostsList:
        """Returns the list of boosts that were applied to a channel or supergroup by a specific user (admins only).

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target channel or supergroup.

            user_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target user.

        Returns:
            :obj:`~pyrogram.raw.base.premium.BoostsList`: The boosts list.

        Example:
            .. code-block:: python

                boosts = await app.get_user_boosts(chat_id, user_id)
        """
        r = await self.resolve_peer(user_id)
        if isinstance(r, raw.types.InputPeerUser):
            user = raw.types.InputUser(user_id=r.user_id, access_hash=r.access_hash)
        elif isinstance(r, raw.types.InputPeerSelf):
            user = raw.types.InputUserSelf()
        else:
            user = r

        return await self.invoke(
            raw.functions.premium.GetUserBoosts(
                peer=await self.resolve_peer(chat_id),
                user_id=user,
            )
        )
