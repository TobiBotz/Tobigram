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
from pyrogram import enums, raw, utils


class ReportChat:
    async def report_chat(
        self: pyrogram.Client,
        chat_id: int | str,
        reason: enums.ReportReason | raw.base.ReportReason | str = enums.ReportReason.SPAM,
        message: str = "",
    ) -> bool:
        """Report a chat (channel, supergroup, group, or user) for rule violations.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            reason (:obj:`~pyrogram.enums.ReportReason` | ``str``, *optional*):
                The reason for reporting. Defaults to :obj:`~pyrogram.enums.ReportReason.SPAM`.

            message (``str``, *optional*):
                Additional explanatory text or details about the report. Defaults to "" (empty string).

        Returns:
            ``bool``: True on success.

        Example:
            .. code-block:: python

                from pyrogram.enums import ReportReason

                # Report a spam group
                await app.report_chat(chat_id, ReportReason.SPAM)

                # Report a scam/impersonation channel with description
                await app.report_chat(chat_id, ReportReason.FAKE, "Impersonating official channel")
        """
        peer = await self.resolve_peer(chat_id)
        parsed_reason = utils.parse_report_reason(reason)

        return bool(
            await self.invoke(
                raw.functions.account.ReportPeer(
                    peer=peer,
                    reason=parsed_reason,
                    message=message,
                )
            )
        )
