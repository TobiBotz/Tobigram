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

from collections.abc import AsyncGenerator

import pyrogram
from pyrogram import raw, types


class GetStarsTransactions:
    async def get_stars_transactions(
        self: pyrogram.Client,
        chat_id: int | str | None = None,
        inbound: bool | None = None,
        outbound: bool | None = None,
        ascending: bool = False,
        ton: bool = False,
        subscription_id: str | None = None,
        limit: int = 0,
    ) -> AsyncGenerator[types.StarsTransaction, None] | None:
        """Get the Telegram Stars transaction history for an account, bot, or channel.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            chat_id (``int`` | ``str``, *optional*):
                Unique identifier (int) or username (str) of the target chat, bot, or channel.
                Defaults to None (the current account / "me").

            inbound (``bool``, *optional*):
                Pass True to retrieve only incoming transactions (credits).
                Defaults to None (both incoming and outgoing).

            outbound (``bool``, *optional*):
                Pass True to retrieve only outgoing transactions (debits).
                Defaults to None (both incoming and outgoing).

            ascending (``bool``, *optional*):
                Pass True to sort transactions in ascending order (oldest first).
                Defaults to False (newest first).

            ton (``bool``, *optional*):
                Pass True to retrieve TON transactions instead of Stars.
                Defaults to False.

            subscription_id (``str``, *optional*):
                Filter transactions by a specific star subscription ID.

            limit (``int``, *optional*):
                Limits the number of transactions to be retrieved.
                By default, no limit is applied and all transactions are returned.

        Returns:
            ``Generator``: A generator yielding :obj:`~pyrogram.types.StarsTransaction` objects.

        Example:
            .. code-block:: python

                # Get all stars transactions for the current account
                async for tx in app.get_stars_transactions():
                    print(tx.id, tx.amount, tx.date)

                # Get only incoming stars for a channel or bot
                async for tx in app.get_stars_transactions(chat_id="my_channel", inbound=True, limit=20):
                    print(f"+{tx.amount} from {tx.user.first_name if tx.user else tx.peer}")
        """
        if chat_id is None:
            peer = raw.types.InputPeerSelf()
        else:
            peer = await self.resolve_peer(chat_id)

        current = 0
        total = abs(limit) or (1 << 31) - 1
        sub_limit = min(100, total)
        offset = ""

        while True:
            r = await self.invoke(
                raw.functions.payments.GetStarsTransactions(
                    peer=peer,
                    inbound=inbound,
                    outbound=outbound,
                    ascending=ascending or None,
                    ton=ton or None,
                    subscription_id=subscription_id,
                    offset=offset,
                    limit=sub_limit,
                ),
                sleep_threshold=60,
            )

            if not r.history:
                return

            users = {u.id: u for u in r.users}
            chats = {c.id: c for c in r.chats}

            for item in r.history:
                yield types.StarsTransaction._parse(self, item, users, chats)

                current += 1
                if current >= total:
                    return

            if not getattr(r, "next_offset", None):
                return

            offset = r.next_offset
