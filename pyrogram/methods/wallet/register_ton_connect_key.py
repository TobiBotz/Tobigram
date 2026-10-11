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


class RegisterTonConnectKey:
    async def register_ton_connect_key(
        self: pyrogram.Client,
        session_id: int,
        client_id: str,
    ) -> raw.base.wallet.TonConnectChallenge:
        """Register a client public key for a TON Connect session.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            session_id (``int``):
                The TON Connect session identifier.

            client_id (``str``):
                The client identifier key to register.

        Returns:
            :obj:`~pyrogram.raw.base.wallet.TonConnectChallenge`: The generated challenge payload.

        Example:
            .. code-block:: python

                challenge = await app.register_ton_connect_key(
                    session_id=123456789,
                    client_id="client_key",
                )
        """
        return await self.invoke(
            raw.functions.wallet.TonConnectRegisterKey(
                session_id=session_id,
                client_id=client_id,
            )
        )
