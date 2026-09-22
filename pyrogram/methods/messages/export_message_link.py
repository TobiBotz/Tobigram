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


class ExportMessageLink:
    async def export_message_link(
        self: pyrogram.Client,
        chat_id: int | str,
        message_id: int,
        grouped: bool | None = None,
        thread: bool | None = None,
    ) -> str:
        """Export an HTTP link to a message in a channel or supergroup.

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target channel or supergroup.

            message_id (``int``):
                The message ID to get the link for.

            grouped (``bool``, *optional*):
                Whether to include other media in an album/media group.

            thread (``bool``, *optional*):
                Whether to include the thread context in the link.

        Returns:
            ``str``: On success, the exported HTTP link is returned.

        Example:
            .. code-block:: python

                link = await app.export_message_link(chat_id, 123)
        """
        peer = await self.resolve_peer(chat_id)

        r = await self.invoke(
            raw.functions.channels.ExportMessageLink(
                channel=peer,
                id=message_id,
                grouped=grouped,
                thread=thread,
            )
        )

        return r.link
