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


class StartTonConnectSession:
    async def start_ton_connect_session(
        self: pyrogram.Client,
        dapp_client_id: str,
        manifest_url: str,
    ) -> types.TonConnectSession:
        """Start a new TON Connect session for a decentralized application.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            dapp_client_id (``str``):
                The client identifier of the decentralized application.

            manifest_url (``str``):
                URL to the TON Connect manifest of the decentralized application.

        Returns:
            :obj:`~pyrogram.types.TonConnectSession`: On success, the started TON Connect session is returned.

        Example:
            .. code-block:: python

                session = await app.start_ton_connect_session(
                    dapp_client_id="dapp_123",
                    manifest_url="https://example.com/tonconnect-manifest.json",
                )
        """
        r = await self.invoke(
            raw.functions.wallet.TonConnectCreateSession(
                dapp_client_id=dapp_client_id,
                manifest_url=manifest_url,
            )
        )
        return types.TonConnectSession._parse(self, r)