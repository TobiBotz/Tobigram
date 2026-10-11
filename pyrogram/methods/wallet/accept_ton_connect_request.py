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


class AcceptTonConnectRequest:
    async def accept_ton_connect_request(
        self: pyrogram.Client,
        session_id: int,
        msg_id: int,
        app_request_id: str,
        *,
        challenge_answer: bytes | None = None,
        declined: bool = False,
    ) -> bool:
        """Accept a pending TON Connect request from a connected dApp.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            session_id (``int``):
                The TON Connect session identifier.

            msg_id (``int``):
                Message identifier of the request.

            app_request_id (``str``):
                Application request identifier.

            challenge_answer (``bytes``, *optional*):
                Challenge answer if signing/confirming the request.

            declined (``bool``, *optional*):
                Whether the request was declined. Defaults to False.

        Returns:
            ``bool``: True on success.

        Example:
            .. code-block:: python

                ok = await app.accept_ton_connect_request(
                    session_id=123,
                    msg_id=456,
                    app_request_id="req_1",
                    challenge_answer=b"...",
                )
        """
        return await self.invoke(
            raw.functions.wallet.TonConnectClaimRequest(
                session_id=session_id,
                msg_id=msg_id,
                app_request_id=app_request_id,
                challenge_answer=challenge_answer,
                declined=declined,
            )
        )

    # Backward compatibility alias
    claim_ton_connect_request = accept_ton_connect_request
