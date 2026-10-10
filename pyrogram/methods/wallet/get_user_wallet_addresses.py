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


class GetUserWalletAddresses:
    async def get_user_wallet_addresses(
        self: pyrogram.Client,
        users: list[int | str],
        addresses: list[str] | None = None,
        force: bool | None = None,
    ) -> raw.base.wallet.UserAddresses:
        """Resolve wallet addresses and public keys for a list of users.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            users (List of ``int`` | ``str``):
                List of user IDs or usernames to resolve.

            addresses (List of ``str``, *optional*):
                List of known addresses to query.

            force (``bool``, *optional*):
                Whether to force cache invalidation.

        Returns:
            :obj:`~pyrogram.raw.base.wallet.UserAddresses`: On success, the user wallet addresses are returned.

        Example:
            .. code-block:: python

                addrs = await app.get_user_wallet_addresses(["username"])
                print(addrs)
        """
        input_users = [await self.resolve_peer(u) for u in users]
        return await self.invoke(
            raw.functions.wallet.GetUserAddresses(
                id=input_users,
                addresses=addresses or [],
                force=force,
            )
        )
