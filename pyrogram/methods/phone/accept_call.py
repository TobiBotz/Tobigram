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


class AcceptCall:
    async def accept_call(
        self: pyrogram.Client,
        call_id: int,
        access_hash: int,
        g_b: bytes,
        protocol: raw.base.PhoneCallProtocol,
    ) -> raw.base.phone.PhoneCall:
        """Accept an incoming 1-on-1 private phone call.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            call_id (``int``):
                The unique phone call ID.

            access_hash (``int``):
                The access hash of the phone call.

            g_b (``bytes``):
                Diffie-Hellman public key exchange parameter.

            protocol (:obj:`~pyrogram.raw.base.PhoneCallProtocol`):
                VoIP call protocol settings.

        Returns:
            :obj:`~pyrogram.raw.base.phone.PhoneCall`: The accepted phone call object.

        Example:
            .. code-block:: python

                call = await app.accept_call(call_id=123, access_hash=456, g_b=b"...", protocol=protocol)
        """
        return await self.invoke(
            raw.functions.phone.AcceptCall(
                peer=raw.types.InputPhoneCall(id=call_id, access_hash=access_hash),
                g_b=g_b,
                protocol=protocol,
            )
        )
