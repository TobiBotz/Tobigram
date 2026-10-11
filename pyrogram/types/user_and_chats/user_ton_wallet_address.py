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

from pyrogram import raw, types
from ..object import Object

if TYPE_CHECKING:
    import pyrogram


class UserTonWalletAddress(Object):
    """Contains TON wallet address information of a user.

    Parameters:
        wallet_address (``str``):
            Address of the user's wallet in the TON blockchain.

        public_key (``bytes``):
            Public key of the wallet address.

        user (:obj:`~pyrogram.types.User`, *optional*):
            User object associated with this wallet address, if resolved.
    """

    def __init__(
        self,
        *,
        client: pyrogram.Client | None = None,
        wallet_address: str,
        public_key: bytes,
        user: types.User | None = None,
    ):
        super().__init__(client)

        self.wallet_address = wallet_address
        self.public_key = public_key
        self.user = user

    @staticmethod
    def _parse(
        client: pyrogram.Client,
        address: raw.types.WalletUserAddress,
        users: dict[int, raw.types.User] | None = None,
    ) -> UserTonWalletAddress | None:
        if not address:
            return None

        parsed_user = None
        if users and address.user_id and address.user_id in users:
            parsed_user = types.User._parse(client, users[address.user_id])

        return UserTonWalletAddress(
            client=client,
            wallet_address=address.address,
            public_key=address.public_key,
            user=parsed_user,
        )
