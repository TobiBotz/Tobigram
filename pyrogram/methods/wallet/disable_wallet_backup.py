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


class DisableWalletBackup:
    async def disable_wallet_backup(
        self: pyrogram.Client,
        password: str | raw.base.InputCheckPasswordSRP | None = None,
        new_public_key: bytes | None = None,
        proof: raw.base.WalletOwnershipProof | None = None,
    ) -> types.WalletState:
        """Disable distributed cloud backup for the wallet.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            password (``str`` | :obj:`~pyrogram.raw.base.InputCheckPasswordSRP`, *optional*):
                Two-step verification 2FA password.

            new_public_key (``bytes``, *optional*):
                New public key for the wallet.

            proof (:obj:`~pyrogram.raw.base.WalletOwnershipProof`, *optional*):
                Wallet ownership cryptographic proof.

        Returns:
            :obj:`~pyrogram.types.WalletState`: On success, the updated wallet state is returned.

        Example:
            .. code-block:: python

                state = await app.disable_wallet_backup()
        """
        pwd = await self.check_password(password) if isinstance(password, str) else password

        r = await self.invoke(
            raw.functions.wallet.DisableBackup(
                password=pwd,
                new_public_key=new_public_key,
                proof=proof,
            )
        )
        return types.WalletState._parse(self, r)

