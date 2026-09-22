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


class IsEligibleToJoinSmsJobs:
    async def is_eligible_to_join_sms_jobs(
        self: pyrogram.Client,
    ) -> raw.base.smsjobs.EligibilityToJoin:
        """Check if we can process SMS jobs (official clients only).

        .. include:: /_includes/usable-by/users.rst

        Returns:
            :obj:`~pyrogram.raw.base.smsjobs.EligibilityToJoin`: The eligibility status.

        Example:
            .. code-block:: python

                eligible = await app.is_eligible_to_join_sms_jobs()
        """
        return await self.invoke(raw.functions.smsjobs.IsEligibleToJoin())
