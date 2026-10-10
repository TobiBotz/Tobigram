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


class SendWalletTransfer:
    async def send_wallet_transfer(
        self: pyrogram.Client,
        user_id: int | str,
        data_normal: bytes,
        data_gasless: bytes | None = None,
        random_id: int | None = None,
    ) -> raw.base.Updates:
        """Submit a cryptocurrency transfer from the wallet, optionally using gasless relaying.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            user_id (``int`` | ``str``):
                Target user identifier (ID or username).

            data_normal (``bytes``):
                Normal transfer payload bytes.

            data_gasless (``bytes``, *optional*):
                Gasless transfer payload bytes.

            random_id (``int``, *optional*):
                Unique 64-bit random ID. Defaults to auto-generated.

        Returns:
            :obj:`~pyrogram.raw.base.Updates`: On success, updates confirming the transfer are returned.

        Example:
            .. code-block:: python

                updates = await app.send_wallet_transfer(
                    user_id=123456,
                    data_normal=b"...",
                )
                print(updates)
        """
        peer = await self.resolve_peer(user_id)
        return await self.invoke(
            raw.functions.wallet.SendTransfer(
                user_id=peer,
                data_normal=data_normal,
                data_gasless=data_gasless,
                random_id=random_id if random_id is not None else self.rnd_id(),
            )
        )
