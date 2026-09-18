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


class ReportAntiSpamFalsePositive:
    async def report_anti_spam_false_positive(
        self: pyrogram.Client,
        chat_id: int | str,
        message_id: int,
    ) -> bool:
        """Report a false positive action by Telegram's native automated anti-spam system in a supergroup.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target channel/supergroup.

            message_id (``int``):
                Unique identifier of the incorrectly flagged message.

        Returns:
            ``bool``: True on success.

        Example:
            .. code-block:: python

                # Report a false positive
                await app.report_anti_spam_false_positive(chat_id, message_id)
        """
        peer = await self.resolve_peer(chat_id)
        if not isinstance(
            peer, (raw.types.InputPeerChannel, raw.types.InputPeerChannelFromMessage)
        ):
            raise ValueError("Target chat must be a supergroup or channel")

        return bool(
            await self.invoke(
                raw.functions.channels.ReportAntiSpamFalsePositive(
                    channel=utils.get_input_channel(peer),
                    msg_id=message_id,
                )
            )
        )
