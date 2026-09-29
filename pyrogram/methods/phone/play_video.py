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
from pyrogram import types


class PlayVideo:
    async def play_video(
        self: pyrogram.Client,
        chat_id: int | str,
        video: str | types.MediaStream,
    ) -> types.GroupCall:
        """Stream a video file or remote stream into group voice chat.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            video (``str`` | :obj:`~pyrogram.types.MediaStream`):
                Path to the video file (e.g. MP4, MKV) or a MediaStream descriptor.

        Returns:
            :obj:`~pyrogram.types.GroupCall`: On success, group call information is returned.

        Example:
            .. code-block:: python

                # Play local MP4 video
                await app.play_video(chat_id, "video.mp4")
        """
        if isinstance(video, str):
            media = types.MediaStream(path=video, video=True)
        else:
            media = video

        return await self.calls.play(chat_id=chat_id, media=media)
