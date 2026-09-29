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


class AcceptAuthorization:
    async def accept_authorization(
        self: pyrogram.Client,
        bot_id: int,
        scope: str,
        public_key: str,
        value_hashes: list[raw.base.SecureValueHash],
        credentials: raw.base.SecureCredentialsEncrypted,
    ) -> bool:
        """Accept a Telegram Passport authorization request and send requested values.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            bot_id (``int``):
                User identifier of the service's bot.

            scope (``str``):
                Telegram Passport element types requested by the service.

            public_key (``str``):
                Service's public key.

            value_hashes (List of :obj:`~pyrogram.raw.base.SecureValueHash`):
                Encrypted value hashes.

            credentials (:obj:`~pyrogram.raw.base.SecureCredentialsEncrypted`):
                Encrypted credentials.

        Returns:
            ``bool``: On success, True is returned.
        """
        return await self.invoke(
            raw.functions.account.AcceptAuthorization(
                bot_id=bot_id,
                scope=scope,
                public_key=public_key,
                value_hashes=value_hashes,
                credentials=credentials,
            )
        )
