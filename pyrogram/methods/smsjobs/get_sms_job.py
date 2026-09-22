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


class GetSmsJob:
    async def get_sms_job(
        self: pyrogram.Client,
        job_id: str,
    ) -> raw.base.SmsJob:
        """Get info about an SMS job (official clients only).

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            job_id (``str``):
                Job ID.

        Returns:
            :obj:`~pyrogram.raw.base.SmsJob`: The SMS job info.

        Example:
            .. code-block:: python

                job = await app.get_sms_job(job_id)
        """
        return await self.invoke(
            raw.functions.smsjobs.GetSmsJob(
                job_id=job_id,
            )
        )
