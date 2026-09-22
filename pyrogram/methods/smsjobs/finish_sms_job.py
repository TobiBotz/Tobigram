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


class FinishSmsJob:
    async def finish_sms_job(
        self: pyrogram.Client,
        job_id: str,
        error: str | None = None,
    ) -> bool:
        """Finish an SMS job (official clients only).

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            job_id (``str``):
                Job ID.

            error (``str``, *optional*):
                If failed, the error reason.

        Returns:
            ``bool``: True on success.

        Example:
            .. code-block:: python

                await app.finish_sms_job(job_id)
        """
        return bool(
            await self.invoke(
                raw.functions.smsjobs.FinishJob(
                    job_id=job_id,
                    error=error,
                )
            )
        )
