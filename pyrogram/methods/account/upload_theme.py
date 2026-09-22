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


class UploadTheme:
    async def upload_theme(
        self: pyrogram.Client,
        file: raw.base.InputFile,
        file_name: str,
        mime_type: str,
        thumb: raw.base.InputFile | None = None,
    ) -> raw.base.Document:
        """Upload a theme file with platform-specific colors.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            file (:obj:`~pyrogram.raw.base.InputFile`):
                Previously uploaded theme file with platform-specific colors for UI components.

            file_name (``str``):
                File name.

            mime_type (``str``):
                MIME type, must be application/x-tgtheme-{format}, where format depends on the client.

            thumb (:obj:`~pyrogram.raw.base.InputFile`, *optional*):
                Thumbnail.

        Returns:
            :obj:`~pyrogram.raw.base.Document`: On success, the document is returned.
        """
        return await self.invoke(
            raw.functions.account.UploadTheme(
                file=file,
                file_name=file_name,
                mime_type=mime_type,
                thumb=thumb,
            )
        )
