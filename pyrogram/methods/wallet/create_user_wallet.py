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


class CreateUserWallet:
    async def create_user_wallet(
        self: pyrogram.Client,
        user_id: int | str,
    ) -> types.UserTonWalletAddress | None:
        """Create or resolve a TON wallet address for the specified regular user.

        .. include:: /_includes/usable-by/users-and-bots.rst

        Parameters:
            user_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target user.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".

        Returns:
            :obj:`~pyrogram.types.UserTonWalletAddress` | ``None``: On success, information about the created/resolved user wallet address is returned.

        Example:
            .. code-block:: python

                wallet = await app.create_user_wallet("username")
                print(wallet.wallet_address)
        """
        r = await self.invoke(
            raw.functions.wallet.GetUserAddresses(
                id=[await self.resolve_peer(user_id)],
                addresses=[],
                force=True,
            )
        )

        if not r.addresses:
            return None

        users = {u.id: u for u in r.users}
        return types.UserTonWalletAddress._parse(self, r.addresses[0], users)
