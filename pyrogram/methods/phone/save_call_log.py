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


class SaveCallLog:
    async def save_call_log(
        self: pyrogram.Client,
        call_id: int,
        access_hash: int,
        file: str | raw.base.InputFile,
    ) -> bool:
        """Upload VoIP phone call log file.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            call_id (``int``):
                The unique phone call ID.

            access_hash (``int``):
                The access hash of the phone call.

            file (``str`` | :obj:`~pyrogram.raw.base.InputFile`):
                Log file path or InputFile object.

        Returns:
            ``bool``: On success, True is returned.

        Example:
            .. code-block:: python

                await app.save_call_log(call_id=123, access_hash=456, file="voip.log")
        """
        if isinstance(file, str):
            file = await self.save_file(file)

        return await self.invoke(
            raw.functions.phone.SaveCallLog(
                peer=raw.types.InputPhoneCall(id=call_id, access_hash=access_hash),
                file=file,
            )
        )
