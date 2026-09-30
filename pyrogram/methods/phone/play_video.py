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

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pyrogram
    from pyrogram import types


class PlayVideo:
    async def play_video(
        self: pyrogram.Client,
        chat_id: int | str,
        video: (
            str
            | types.MediaStream
            | types.Message
            | types.Video
            | types.Animation
            | types.Document
        ),
    ) -> types.GroupCall:
        """Stream a video file, remote stream, or Telegram media directly into group voice chat.

        Telegram media objects (:obj:`~pyrogram.types.Message`, :obj:`~pyrogram.types.Video`,
        :obj:`~pyrogram.types.Animation`, :obj:`~pyrogram.types.Document`, or file ID strings) are
        streamed directly in-memory on-the-fly with ZERO disk footprint.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            video (``str`` | :obj:`~pyrogram.types.MediaStream` | :obj:`~pyrogram.types.Message` | :obj:`~pyrogram.types.Video` | :obj:`~pyrogram.types.Animation` | :obj:`~pyrogram.types.Document`):
                Path to the video file (e.g. MP4, MKV), MediaStream descriptor, or Telegram media object.

        Returns:
            :obj:`~pyrogram.types.GroupCall`: On success, group call information is returned.

        Example:
            .. code-block:: python

                # Play local MP4 video
                await app.play_video(chat_id, "video.mp4")

                # Play Telegram video directly without downloading to disk
                await app.play_video(chat_id, message.video)
                await app.play_video(chat_id, message)
        """
        return await self.calls.play(chat_id=chat_id, media=video, video=True)
