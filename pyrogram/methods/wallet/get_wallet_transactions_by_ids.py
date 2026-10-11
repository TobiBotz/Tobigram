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


class GetWalletTransactionsByIds:
    async def get_wallet_transactions_by_ids(
        self: pyrogram.Client,
        ids: list[str],
    ) -> list[types.WalletTransaction]:
        """Fetch wallet transactions by their identifiers.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            ids (List of ``str``):
                List of transaction identifiers.

        Returns:
            List of :obj:`~pyrogram.types.WalletTransaction`: On success, the transactions are returned.

        Example:
            .. code-block:: python

                txs = await app.get_wallet_transactions_by_ids(["tx_1", "tx_2"])
        """
        r = await self.invoke(raw.functions.wallet.GetTransactionsByIDs(id=ids))
        users = {u.id: u for u in r.users}
        return [types.WalletTransaction._parse(self, tx, users) for tx in r.transactions]

