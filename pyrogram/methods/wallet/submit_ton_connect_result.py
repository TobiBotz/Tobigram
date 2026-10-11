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


class SubmitTonConnectResult:
    async def submit_ton_connect_result(
        self: pyrogram.Client,
        session_id: int,
        challenge_answer: bytes,
        body: bytes,
        trace_id: str | None = None,
        error: bool | None = None,
    ) -> bool:
        """Send the connection result back to a TON Connect session.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            session_id (``int``):
                The TON Connect session identifier.

            challenge_answer (``bytes``):
                Cryptographic answer proving ownership.

            body (``bytes``):
                Payload data or connection result payload.

            trace_id (``str``, *optional*):
                Optional tracing identifier.

            error (``bool``, *optional*):
                Whether this result indicates an error.

        Returns:
            ``bool``: True on success.

        Example:
            .. code-block:: python

                ok = await app.submit_ton_connect_result(
                    session_id=123456789,
                    challenge_answer=b"...",
                    body=b"...",
                )
        """
        return await self.invoke(
            raw.functions.wallet.TonConnectSubmitConnectResult(
                session_id=session_id,
                challenge_answer=challenge_answer,
                body=body,
                trace_id=trace_id,
                error=error,
            )
        )
