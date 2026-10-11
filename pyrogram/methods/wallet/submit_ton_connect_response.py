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


class SubmitTonConnectResponse:
    async def submit_ton_connect_response(
        self: pyrogram.Client,
        session_id: int,
        msg_id: int,
        body: bytes,
        *,
        trace_id: str | None = None,
    ) -> bool:
        """Submit the response payload for a processed TON Connect request.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            session_id (``int``):
                The TON Connect session identifier.

            msg_id (``int``):
                Message identifier of the request.

            body (``bytes``):
                Response payload data.

            trace_id (``str``, *optional*):
                Optional tracing identifier.

        Returns:
            ``bool``: True on success.

        Example:
            .. code-block:: python

                ok = await app.submit_ton_connect_response(
                    session_id=123,
                    msg_id=456,
                    body=b"...",
                )
        """
        return await self.invoke(
            raw.functions.wallet.TonConnectSubmitResponse(
                session_id=session_id,
                msg_id=msg_id,
                body=body,
                trace_id=trace_id,
            )
        )
