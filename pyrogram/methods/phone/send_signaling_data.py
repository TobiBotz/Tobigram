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


class SendSignalingData:
    async def send_signaling_data(
        self: pyrogram.Client,
        call_id: int,
        access_hash: int,
        data: bytes,
    ) -> bool:
        """Send VoIP signaling data (e.g. ICE candidates) for an ongoing phone call.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            call_id (``int``):
                The unique phone call ID.

            access_hash (``int``):
                The access hash of the phone call.

            data (``bytes``):
                WebRTC signaling payload.

        Returns:
            ``bool``: On success, True is returned.

        Example:
            .. code-block:: python

                await app.send_signaling_data(call_id=123, access_hash=456, data=b"...")
        """
        return await self.invoke(
            raw.functions.phone.SendSignalingData(
                peer=raw.types.InputPhoneCall(id=call_id, access_hash=access_hash),
                data=data,
            )
        )
