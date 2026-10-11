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


class FetchEncryptedSecretPhrasePart:
    async def fetch_encrypted_secret_phrase_part(
        self: pyrogram.Client,
        token: str,
        public_key: bytes,
    ) -> raw.base.wallet.EncryptedSecretPhrasePart:
        """Retrieve an encrypted secret phrase shard stored on a specific data center.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            token (``str``):
                The export token received from :meth:`~pyrogram.Client.export_wallet_secret_phrase`.

            public_key (``bytes``):
                Public key associated with the backup shard.

        Returns:
            :obj:`~pyrogram.raw.base.wallet.EncryptedSecretPhrasePart`: The encrypted secret phrase part.

        Example:
            .. code-block:: python

                part = await app.fetch_encrypted_secret_phrase_part(token="...", public_key=b"...")
        """
        return await self.invoke(
            raw.functions.wallet.FetchEncryptedSecretPhrasePart(
                token=token,
                public_key=public_key,
            )
        )
