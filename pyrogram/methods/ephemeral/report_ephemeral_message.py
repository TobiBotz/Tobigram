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


class ReportEphemeralMessage:
    async def report_ephemeral_message(
        self: pyrogram.Client,
        chat_id: int | str,
        message_id: int,
        option: bytes | str,
        message: str = "",
    ) -> raw.base.ReportResult:
        """Report an ephemeral message.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            message_id (``int``):
                Identifier of the ephemeral message to report.

            option (``bytes`` | ``str``):
                Report option identifier.

            message (``str``, *optional*):
                Comment or explanation for the report. Defaults to empty string.

        Returns:
            :obj:`~pyrogram.raw.base.ReportResult`: Report result.

        Example:
            .. code-block:: python

                result = await app.report_ephemeral_message(chat_id, message_id, b"spam", "Spam message")
        """
        if isinstance(option, str):
            option = option.encode()

        return await self.invoke(
            raw.functions.ephemeral.ReportMessage(
                peer=await self.resolve_peer(chat_id),
                id=message_id,
                option=option,
                message=message,
            )
        )
