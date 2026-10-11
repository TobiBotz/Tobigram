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

from pyrogram import raw, types, utils
from ..object import Object

if TYPE_CHECKING:
    from datetime import datetime
    import pyrogram


class WalletTransaction(Object):
    """Contains information about a TON wallet blockchain transaction.

    Parameters:
        id (``str``):
            Unique identifier of the transaction.

        amount (``int``):
            Transaction amount in nano-TON.

        fee (``int``):
            Transaction fee in nano-TON.

        date (:py:obj:`~datetime.datetime`):
            Date of the transaction.

        is_incoming (``bool``):
            True if this is an incoming transfer.

        is_gasless (``bool``):
            True if this was a gasless transfer.

        is_failed (``bool``):
            True if the transaction failed.

        is_key_change (``bool``):
            True if this transaction modified the wallet key.

        comment (``str``, *optional*):
            Transaction comment or transfer memo.

        comment_encrypted (``bool``, *optional*):
            True if the transaction comment was encrypted.

        tx_hash (``str``, *optional*):
            Blockchain transaction hash.

        peer_user (:obj:`~pyrogram.types.User`, *optional*):
            Telegram user counterpart if transferred to/from a user.

        peer_address (``str``, *optional*):
            Blockchain wallet address counterpart.

        peer_domain (``str``, *optional*):
            TON DNS domain associated with the peer address.

        onramp_provider (``str``, *optional*):
            Name of the fiat onramp provider if purchased via onramp.
    """

    def __init__(
        self,
        *,
        client: pyrogram.Client | None = None,
        id: str,
        amount: int,
        fee: int,
        date: datetime,
        is_incoming: bool = False,
        is_gasless: bool = False,
        is_failed: bool = False,
        is_key_change: bool = False,
        comment: str | None = None,
        comment_encrypted: bool = False,
        tx_hash: str | None = None,
        peer_user: types.User | None = None,
        peer_address: str | None = None,
        peer_domain: str | None = None,
        onramp_provider: str | None = None,
    ):
        super().__init__(client)

        self.id = id
        self.amount = amount
        self.fee = fee
        self.date = date
        self.is_incoming = is_incoming
        self.is_gasless = is_gasless
        self.is_failed = is_failed
        self.is_key_change = is_key_change
        self.comment = comment
        self.comment_encrypted = comment_encrypted
        self.tx_hash = tx_hash
        self.peer_user = peer_user
        self.peer_address = peer_address
        self.peer_domain = peer_domain
        self.onramp_provider = onramp_provider

    @property
    def amount_ton(self) -> float:
        """Transaction amount converted to TON."""
        return self.amount / 1_000_000_000

    @property
    def fee_ton(self) -> float:
        """Transaction fee converted to TON."""
        return self.fee / 1_000_000_000

    @staticmethod
    def _parse(
        client: pyrogram.Client,
        tx: raw.types.WalletTransaction,
        users: dict[int, raw.types.User] | None = None,
    ) -> WalletTransaction | None:
        if not tx:
            return None

        peer_user = None
        peer_address = None
        peer_domain = None
        onramp_provider = None

        if isinstance(tx.peer, raw.types.WalletTransactionPeerUser):
            if users and tx.peer.user_id in users:
                peer_user = types.User._parse(client, users[tx.peer.user_id])
            peer_address = tx.peer.address
            peer_domain = tx.peer.domain
        elif isinstance(tx.peer, raw.types.WalletTransactionPeerAddress):
            peer_address = tx.peer.address
            peer_domain = tx.peer.domain
        elif isinstance(tx.peer, raw.types.WalletTransactionPeerOnramp):
            peer_address = tx.peer.address
            peer_domain = tx.peer.domain
            onramp_provider = tx.peer.provider_name

        return WalletTransaction(
            client=client,
            id=tx.id,
            amount=tx.amount,
            fee=tx.fee,
            date=utils.timestamp_to_datetime(tx.date),
            is_incoming=bool(tx.incoming),
            is_gasless=bool(tx.gasless),
            is_failed=bool(tx.failed),
            is_key_change=bool(tx.key_change),
            comment=tx.comment,
            comment_encrypted=bool(tx.comment_encrypted),
            tx_hash=tx.tx_hash,
            peer_user=peer_user,
            peer_address=peer_address,
            peer_domain=peer_domain,
            onramp_provider=onramp_provider,
        )
