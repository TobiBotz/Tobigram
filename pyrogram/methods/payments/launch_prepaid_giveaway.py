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


class LaunchPrepaidGiveaway:
    async def launch_prepaid_giveaway(
        self: pyrogram.Client,
        chat_id: int | str,
        giveaway_id: int,
        purpose: raw.base.InputStorePaymentPurpose,
    ) -> raw.types.Updates:
        """Launch a previously prepaid giveaway in a channel.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Target channel/chat ID.

            giveaway_id (``int``):
                Prepaid giveaway identifier.

            purpose (:obj:`~pyrogram.raw.base.InputStorePaymentPurpose`):
                Payment purpose specification.

        Returns:
            :obj:`~pyrogram.raw.types.Updates`: On success, updates are returned.

        Example:
            .. code-block:: python

                await app.launch_prepaid_giveaway(channel_id, giveaway_id, purpose)
        """
        peer = await self.resolve_peer(chat_id)

        return await self.invoke(
            raw.functions.payments.LaunchPrepaidGiveaway(
                peer=peer,
                giveaway_id=giveaway_id,
                purpose=purpose,
            )
        )
