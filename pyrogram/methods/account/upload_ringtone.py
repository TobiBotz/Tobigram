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


class UploadRingtone:
    async def upload_ringtone(
        self: pyrogram.Client,
        file: raw.base.InputFile,
        file_name: str,
        mime_type: str,
    ) -> raw.base.Document:
        """Upload a notification sound.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            file (:obj:`~pyrogram.raw.base.InputFile`):
                Notification sound file.

            file_name (``str``):
                File name.

            mime_type (``str``):
                MIME type of file.

        Returns:
            :obj:`~pyrogram.raw.base.Document`: On success, the uploaded document is returned.
        """
        return await self.invoke(
            raw.functions.account.UploadRingtone(
                file=file,
                file_name=file_name,
                mime_type=mime_type,
            )
        )
