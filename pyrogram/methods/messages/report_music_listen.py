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


class ReportMusicListen:
    async def report_music_listen(
        self: pyrogram.Client,
        message_id: int,
        listened_duration: int,
    ) -> bool:
        """Report that the user listened to a music message (for analytics).

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            message_id (``int``):
                The message ID of the music.

            listened_duration (``int``):
                How many seconds of the track were listened to.

        Returns:
            ``bool``: True on success.

        Example:
            .. code-block:: python

                await app.report_music_listen(message_id=123, listened_duration=60)
        """
        return await self.invoke(
            raw.functions.messages.ReportMusicListen(
                id=message_id,
                listened_duration=listened_duration,
            )
        )
