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
from pyrogram import raw


class ExportWalletSecretPhrase:
    async def export_wallet_secret_phrase(
        self: pyrogram.Client,
        password: str | raw.base.InputCheckPasswordSRP | None = None,
    ) -> raw.base.wallet.SecretPhraseParts:
        """Initiate the export of the wallet recovery secret phrase.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            password (``str`` | :obj:`~pyrogram.raw.base.InputCheckPasswordSRP`, *optional*):
                Two-step verification 2FA password, if enabled on the account.

        Returns:
            :obj:`~pyrogram.raw.base.wallet.SecretPhraseParts`: On success, the secret phrase parts metadata is returned.

        Example:
            .. code-block:: python

                parts = await app.export_wallet_secret_phrase(password="my_password")
        """
        pwd = await self.check_password(password) if isinstance(password, str) else password

        return await self.invoke(
            raw.functions.wallet.ExportSecretPhrase(
                password=pwd,
            )
        )
