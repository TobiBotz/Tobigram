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


class GetWalletTransactionsByMsgHash:
    async def get_wallet_transactions_by_msg_hash(
        self: pyrogram.Client,
        msg_hashes: list[str],
    ) -> list[types.WalletTransaction]:
        """Fetch wallet transactions by message hashes.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            msg_hashes (List of ``str``):
                List of message hashes.

        Returns:
            List of :obj:`~pyrogram.types.WalletTransaction`: On success, the transactions are returned.

        Example:
            .. code-block:: python

                txs = await app.get_wallet_transactions_by_msg_hash(["hash_1", "hash_2"])
        """
        r = await self.invoke(raw.functions.wallet.GetTransactionsByMsgHash(msg_hash=msg_hashes))
        users = {u.id: u for u in r.users}
        return [types.WalletTransaction._parse(self, tx, users) for tx in r.transactions]

