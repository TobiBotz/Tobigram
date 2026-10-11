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


class ImportWallet:
    async def import_wallet(
        self: pyrogram.Client,
        public_key: bytes,
        proof: raw.base.WalletOwnershipProof,
        anchor_public_key: bytes | None = None,
        password: str | raw.base.InputCheckPasswordSRP | None = None,
    ) -> types.WalletState:
        """Import an existing external TON wallet into the account.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            public_key (``bytes``):
                Public key bytes of the wallet being imported.

            proof (:obj:`~pyrogram.raw.base.WalletOwnershipProof`):
                Cryptographic ownership proof of the wallet.

            anchor_public_key (``bytes``, *optional*):
                Anchor public key bytes, if applicable.

            password (``str`` | :obj:`~pyrogram.raw.base.InputCheckPasswordSRP`, *optional*):
                Two-step verification 2FA password, if enabled on the account.

        Returns:
            :obj:`~pyrogram.types.WalletState`: On success, the updated wallet state is returned.

        Example:
            .. code-block:: python

                state = await app.import_wallet(public_key=b"...", proof=proof)
                print(state.address)
        """
        return await self.replace_wallet(
            wallet=raw.types.InputWalletImported(
                public_key=public_key,
                anchor_public_key=anchor_public_key,
                proof=proof,
            ),
            password=password,
        )

