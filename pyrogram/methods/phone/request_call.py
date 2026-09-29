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
from pyrogram import raw, utils


class RequestCall:
    async def request_call(
        self: pyrogram.Client,
        user_id: int | str,
        g_a_hash: bytes,
        protocol: raw.base.PhoneCallProtocol,
        video: bool | None = None,
        random_id: int | None = None,
    ) -> raw.base.phone.PhoneCall:
        """Start a 1-on-1 private phone call.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            user_id (``int`` | ``str``):
                Target user ID or username to call.

            g_a_hash (``bytes``):
                Diffie-Hellman encryption hash for E2E voice call.

            protocol (:obj:`~pyrogram.raw.base.PhoneCallProtocol`):
                VoIP call protocol settings.

            video (``bool``, *optional*):
                Pass True to request a video call.

            random_id (``int``, *optional*):
                Unique random ID for deduplication. Defaults to a random integer.

        Returns:
            :obj:`~pyrogram.raw.base.phone.PhoneCall`: The initiated phone call object.

        Example:
            .. code-block:: python

                call = await app.request_call(user_id=12345678, g_a_hash=b"...", protocol=protocol)
        """
        user = await self.resolve_peer(user_id)
        return await self.invoke(
            raw.functions.phone.RequestCall(
                user_id=utils.get_input_user(user),
                random_id=random_id if random_id is not None else self.rnd_id(),
                g_a_hash=g_a_hash,
                protocol=protocol,
                video=video,
            )
        )
