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


class GetTonConnectPending:
    async def get_ton_connect_pending(
        self: pyrogram.Client,
        *,
        dapp_client_id: str | None = None,
        session_id: int | None = None,
    ) -> raw.base.wallet.TonConnectPending:
        """Retrieve pending requests for a TON Connect session.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            dapp_client_id (``str``, *optional*):
                Client identifier of the dApp.

            session_id (``int``, *optional*):
                Session identifier.

        Returns:
            :obj:`~pyrogram.raw.base.wallet.TonConnectPending`: Pending TON Connect requests.

        Example:
            .. code-block:: python

                pending = await app.get_ton_connect_pending(session_id=123456789)
        """
        return await self.invoke(
            raw.functions.wallet.TonConnectGetPending(
                dapp_client_id=dapp_client_id,
                session_id=session_id,
            )
        )
