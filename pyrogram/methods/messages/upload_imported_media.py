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


class UploadImportedMedia:
    async def upload_imported_media(
        self: pyrogram.Client,
        chat_id: int | str,
        import_id: int,
        file_name: str,
        media: raw.base.InputMedia,
    ) -> raw.base.MessageMedia:
        """Upload a media file for a history import session.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                The target chat.

            import_id (``int``):
                The import session ID from :meth:`~pyrogram.Client.init_history_import`.

            file_name (``str``):
                The original file name of the media.

            media (:obj:`~pyrogram.raw.base.InputMedia`):
                The media to upload.

        Returns:
            :obj:`~pyrogram.raw.base.MessageMedia`: The uploaded media.

        Example:
            .. code-block:: python

                await app.upload_imported_media(chat_id, import_id, "photo.jpg", media)
        """
        peer = await self.resolve_peer(chat_id)

        return await self.invoke(
            raw.functions.messages.UploadImportedMedia(
                peer=peer,
                import_id=import_id,
                file_name=file_name,
                media=media,
            )
        )
