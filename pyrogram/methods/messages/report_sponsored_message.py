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


class ReportSponsoredMessage:
    async def report_sponsored_message(
        self: pyrogram.Client,
        random_id: bytes,
        option: bytes,
    ) -> raw.base.channels.SponsoredMessageReportResult:
        """Report a sponsored message.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            random_id (``bytes``):
                The random ID of the sponsored message.

            option (``bytes``):
                The reporting option chosen by the user.

        Returns:
            :obj:`~pyrogram.raw.base.channels.SponsoredMessageReportResult`: The report result.

        Example:
            .. code-block:: python

                result = await app.report_sponsored_message(random_id, option)
        """
        return await self.invoke(
            raw.functions.messages.ReportSponsoredMessage(random_id=random_id, option=option)
        )
