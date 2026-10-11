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

from typing import TYPE_CHECKING

from pyrogram import raw, utils
from ..object import Object

if TYPE_CHECKING:
    from datetime import datetime
    import pyrogram


class WalletGaslessInfo(Object):
    """Contains information about remaining gasless transactions and relay limits.

    Parameters:
        is_available (``bool``):
            Whether gasless transfers are currently available for this wallet.

        transfers_left (``int``):
            Number of gasless/free transfers remaining in the current quota period.

        reset_at (:py:obj:`~datetime.datetime`):
            Point in time when the gasless transfer quota resets.

        min_amount (``int``):
            Minimum transfer amount in nano-TON required for gasless processing.

        relayer_address (``str``):
            Blockchain wallet address of the relayer node.
    """

    def __init__(
        self,
        *,
        client: pyrogram.Client | None = None,
        is_available: bool,
        transfers_left: int,
        reset_at: datetime,
        min_amount: int,
        relayer_address: str,
    ):
        super().__init__(client)

        self.is_available = is_available
        self.transfers_left = transfers_left
        self.reset_at = reset_at
        self.min_amount = min_amount
        self.relayer_address = relayer_address

    @property
    def min_amount_ton(self) -> float:
        """Minimum transfer amount converted to TON."""
        return self.min_amount / 1_000_000_000

    @staticmethod
    def _parse(
        client: pyrogram.Client,
        info: raw.types.UpdateWalletGaslessInfo | raw.base.Updates,
    ) -> WalletGaslessInfo | None:
        if not info:
            return None

        target = None
        if isinstance(info, raw.types.UpdateWalletGaslessInfo):
            target = info
        elif hasattr(info, "updates"):
            for update in info.updates:
                if isinstance(update, raw.types.UpdateWalletGaslessInfo):
                    target = update
                    break

        if not target:
            return None

        return WalletGaslessInfo(
            client=client,
            is_available=bool(target.available),
            transfers_left=target.left,
            reset_at=utils.timestamp_to_datetime(target.reset_at),
            min_amount=target.min_amount,
            relayer_address=target.relayer_address,
        )
