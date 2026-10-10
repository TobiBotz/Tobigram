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


class GetWalletTransactions:
    async def get_wallet_transactions(
        self: pyrogram.Client,
        offset: str = "",
        limit: int = 100,
        inbound: bool | None = None,
        outbound: bool | None = None,
    ) -> raw.base.wallet.Transactions:
        """Get wallet transaction history.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            offset (``str``, *optional*):
                Offset for pagination. Defaults to "".

            limit (``int``, *optional*):
                Number of transactions to retrieve. Defaults to 100.

            inbound (``bool``, *optional*):
                Filter for inbound transactions.

            outbound (``bool``, *optional*):
                Filter for outbound transactions.

        Returns:
            :obj:`~pyrogram.raw.base.wallet.Transactions`: On success, the transactions list is returned.

        Example:
            .. code-block:: python

                txs = await app.get_wallet_transactions(limit=10)
                print(txs)
        """
        return await self.invoke(
            raw.functions.wallet.GetTransactions(
                offset=offset,
                limit=limit,
                inbound=inbound,
                outbound=outbound,
            )
        )
