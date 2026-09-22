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


class UploadWallPaper:
    async def upload_wall_paper(
        self: pyrogram.Client,
        file: raw.base.InputFile,
        mime_type: str,
        settings: raw.base.WallPaperSettings,
        for_chat: bool | None = None,
    ) -> raw.base.WallPaper:
        """Create and upload a new wallpaper.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            file (:obj:`~pyrogram.raw.base.InputFile`):
                The JPG/PNG wallpaper.

            mime_type (``str``):
                MIME type of uploaded wallpaper.

            settings (:obj:`~pyrogram.raw.base.WallPaperSettings`):
                Wallpaper settings.

            for_chat (``bool``, *optional*):
                Set this flag when uploading wallpapers to be passed to messages.set_chat_wall_paper.

        Returns:
            :obj:`~pyrogram.raw.base.WallPaper`: On success, the wallpaper is returned.
        """
        return await self.invoke(
            raw.functions.account.UploadWallPaper(
                file=file,
                mime_type=mime_type,
                settings=settings,
                for_chat=for_chat,
            )
        )
