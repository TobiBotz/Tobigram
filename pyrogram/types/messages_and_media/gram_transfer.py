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

if TYPE_CHECKING:
    from pyrogram import raw

from ..object import Object


class GramTransfer(Object):
    """A Gram transfer service message.

    Parameters:
        amount (``int``):
            Amount of nano-TON transferred.

        peer_address (``str``):
            Target blockchain address.

        transaction_id (``str``):
            Transaction identifier.

        comment (``str``, *optional*):
            Transfer comment or memo.

        comment_encrypted (``bool``, *optional*):
            Whether the comment is encrypted.
    """

    def __init__(
        self,
        *,
        amount: int,
        peer_address: str,
        transaction_id: str,
        comment: str | None = None,
        comment_encrypted: bool | None = None,
    ):
        super().__init__()

        self.amount = amount
        self.peer_address = peer_address
        self.transaction_id = transaction_id
        self.comment = comment
        self.comment_encrypted = comment_encrypted

    @staticmethod
    def _parse(
        client,
        action: raw.types.MessageActionGramTransfer,
    ) -> GramTransfer:
        return GramTransfer(
            amount=action.amount,
            peer_address=action.peer_address,
            transaction_id=action.transaction_id,
            comment=action.comment,
            comment_encrypted=action.comment_encrypted,
        )
