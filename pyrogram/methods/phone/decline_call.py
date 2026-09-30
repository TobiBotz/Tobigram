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


class DeclineCall:
    async def decline_call(
        self: pyrogram.Client,
        call_id: int,
        access_hash: int,
        duration: int = 0,
        reason: raw.base.PhoneCallDiscardReason | None = None,
        connection_id: int = 0,
        video: bool | None = None,
    ) -> raw.base.Updates:
        """Decline, reject, or hang up a 1-on-1 private phone call.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            call_id (``int``):
                The unique phone call ID.

            access_hash (``int``):
                The access hash of the phone call.

            duration (``int``, *optional*):
                Total call duration in seconds. Defaults to 0.

            reason (:obj:`~pyrogram.raw.base.PhoneCallDiscardReason`, *optional*):
                Why the call was declined or ended. Defaults to :obj:`~pyrogram.raw.types.PhoneCallDiscardReasonHangup`.

            connection_id (``int``, *optional*):
                Preferred relay connection ID. Defaults to 0.

            video (``bool``, *optional*):
                Whether this was a video call.

        Returns:
            :obj:`~pyrogram.raw.base.Updates`: Updates resulting from declining the call.

        Example:
            .. code-block:: python

                # Decline / Hang up a call
                await app.decline_call(call_id=123, access_hash=456, duration=15)
        """
        if reason is None:
            reason = raw.types.PhoneCallDiscardReasonHangup()

        return await self.invoke(
            raw.functions.phone.DiscardCall(
                peer=raw.types.InputPhoneCall(id=call_id, access_hash=access_hash),
                duration=duration,
                reason=reason,
                connection_id=connection_id,
                video=video,
            )
        )
