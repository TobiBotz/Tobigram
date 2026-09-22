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


class InitHistoryImport:
    async def init_history_import(
        self: pyrogram.Client,
        chat_id: int | str,
        file: raw.base.InputFile,
        media_count: int,
    ) -> raw.base.messages.HistoryImport:
        """Initialize a chat history import.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                The chat to import the history into.

            file (:obj:`~pyrogram.raw.base.InputFile`):
                The uploaded history export file.

            media_count (``int``):
                Number of media files to be imported.

        Returns:
            :obj:`~pyrogram.raw.base.messages.HistoryImport`: The history import session.

        Example:
            .. code-block:: python

                session = await app.init_history_import(chat_id, file=uploaded_file, media_count=5)
        """
        peer = await self.resolve_peer(chat_id)

        return await self.invoke(
            raw.functions.messages.InitHistoryImport(
                peer=peer,
                file=file,
                media_count=media_count,
            )
        )
