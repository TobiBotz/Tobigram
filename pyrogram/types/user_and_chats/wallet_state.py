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

from pyrogram import raw
from ..object import Object

if TYPE_CHECKING:
    import pyrogram


class WalletState(Object):
    """Contains information about the native TON wallet state, balance, and backup settings.

    Parameters:
        address (``str``, *optional*):
            Address of the user's wallet in the TON blockchain.

        public_key (``bytes``, *optional*):
            Public key bytes of the wallet.

        balance (``int``, *optional*):
            Current balance in nano-TON.

        backup_enabled (``bool``, *optional*):
            Whether cloud backup is enabled across data centers.

        can_export_phrase (``bool``, *optional*):
            Whether the recovery phrase can be exported.

        can_enable_backup (``bool``, *optional*):
            Whether backup can be enabled for this wallet.

        is_empty (``bool``, *optional*):
            True if the wallet is uninitialized.

        is_creating (``bool``, *optional*):
            True if the wallet is currently being created.
    """

    def __init__(
        self,
        *,
        client: pyrogram.Client | None = None,
        address: str | None = None,
        public_key: bytes | None = None,
        balance: int | None = None,
        backup_enabled: bool | None = None,
        can_export_phrase: bool | None = None,
        can_enable_backup: bool | None = None,
        is_empty: bool | None = None,
        is_creating: bool | None = None,
    ):
        super().__init__(client)

        self.address = address
        self.public_key = public_key
        self.balance = balance
        self.backup_enabled = backup_enabled
        self.can_export_phrase = can_export_phrase
        self.can_enable_backup = can_enable_backup
        self.is_empty = is_empty
        self.is_creating = is_creating

    @property
    def balance_ton(self) -> float:
        """Wallet balance converted to TON."""
        return (self.balance or 0) / 1_000_000_000

    @staticmethod
    def _parse(
        client: pyrogram.Client,
        state: raw.base.WalletState,
    ) -> WalletState | None:
        if not state:
            return None

        if isinstance(state, raw.types.WalletStateEmpty):
            return WalletState(
                client=client,
                is_empty=True,
                is_creating=bool(state.creating),
            )

        if isinstance(state, raw.types.WalletState):
            return WalletState(
                client=client,
                address=state.address,
                public_key=state.public_key,
                balance=state.balance,
                backup_enabled=bool(state.backup_enabled),
                can_export_phrase=bool(state.can_export_phrase),
                can_enable_backup=bool(state.can_enable_backup),
                is_empty=False,
                is_creating=False,
            )

        return None
