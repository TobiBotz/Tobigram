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
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable


class ReportMessages:
    async def report_messages(
        self: pyrogram.Client,
        chat_id: int | str,
        message_ids: int | Iterable[int],
        reason: enums.ReportReason | raw.base.ReportReason | str = enums.ReportReason.SPAM,
        message: str = "",
        option: bytes = b"",
        participant: int | str | None = None,
    ) -> bool:
        """Report specific messages in a chat for rule violations.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            message_ids (``int`` | Iterable of ``int``):
                A single message id or an iterable of message ids to report.

            reason (:obj:`~pyrogram.enums.ReportReason` | ``str``, *optional*):
                The reason for reporting. Defaults to :obj:`~pyrogram.enums.ReportReason.SPAM`.

            message (``str``, *optional*):
                Additional explanatory text or details about the report. Defaults to "" (empty string).

            option (``bytes``, *optional*):
                Specific report option bytes, if known beforehand. Defaults to b"".

            participant (``int`` | ``str``, *optional*):
                Participant peer (user id or username) to report spam for in a channel/supergroup.
                When provided, uses ``channels.ReportSpam``.

        Returns:
            ``bool``: True on success.

        Example:
            .. code-block:: python

                from pyrogram.enums import ReportReason

                # Report a single message
                await app.report_messages(chat_id, 12345, ReportReason.SPAM)

                # Report multiple messages with comment
                await app.report_messages(chat_id, [123, 124], ReportReason.VIOLENCE, "Threatening remarks")
        """
        peer = await self.resolve_peer(chat_id)
        ids = list(message_ids) if not isinstance(message_ids, int) else [message_ids]

        if participant is not None:
            if not isinstance(
                peer, (raw.types.InputPeerChannel, raw.types.InputPeerChannelFromMessage)
            ):
                raise ValueError(
                    "Reporting participant spam is only supported in supergroups/channels"
                )
            return bool(
                await self.invoke(
                    raw.functions.channels.ReportSpam(
                        channel=utils.get_input_channel(peer),
                        participant=await self.resolve_peer(participant),
                        id=ids,
                    )
                )
            )

        if option:
            await self.invoke(
                raw.functions.messages.Report(
                    peer=peer,
                    id=ids,
                    option=option,
                    message=message,
                )
            )
            return True

        res = await self.invoke(
            raw.functions.messages.Report(
                peer=peer,
                id=ids,
                option=b"",
                message="",
            )
        )

        if isinstance(res, raw.types.ReportResultReported):
            return True

        if isinstance(res, raw.types.ReportResultChooseOption):
            target = (
                reason.name.lower()
                if isinstance(reason, enums.ReportReason)
                else str(reason).lower()
            )
            selected_opt = None
            for opt in res.options:
                opt_text = opt.text.lower()
                if target in opt_text or opt_text in target:
                    selected_opt = opt.option
                    break
            if not selected_opt and res.options:
                selected_opt = res.options[0].option

            if selected_opt:
                sub_res = await self.invoke(
                    raw.functions.messages.Report(
                        peer=peer,
                        id=ids,
                        option=selected_opt,
                        message=message,
                    )
                )
                if isinstance(sub_res, raw.types.ReportResultAddComment) and message:
                    await self.invoke(
                        raw.functions.messages.Report(
                            peer=peer,
                            id=ids,
                            option=sub_res.option,
                            message=message,
                        )
                    )

        return True
