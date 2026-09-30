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


class PlayAudio:
    async def play_audio(
        self: pyrogram.Client,
        chat_id: int | str,
        audio: (
            str
            | types.MediaStream
            | types.Message
            | types.Audio
            | types.Voice
            | types.Document
        ),
    ) -> types.GroupCall:
        """Stream an audio file, remote live URL, or Telegram media directly into group voice chat.

        Telegram media objects (:obj:`~pyrogram.types.Message`, :obj:`~pyrogram.types.Audio`,
        :obj:`~pyrogram.types.Voice`, :obj:`~pyrogram.types.Document`, or file ID strings) are
        streamed directly in-memory on-the-fly with ZERO disk footprint.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            audio (``str`` | :obj:`~pyrogram.types.MediaStream` | :obj:`~pyrogram.types.Message` | :obj:`~pyrogram.types.Audio` | :obj:`~pyrogram.types.Voice` | :obj:`~pyrogram.types.Document`):
                Path to the local audio file, live stream URL, MediaStream descriptor, or Telegram media object.
                Telegram media objects are piped directly into the voice chat in RAM without writing to disk.

        Returns:
            :obj:`~pyrogram.types.GroupCall`: On success, group call information is returned.

        Example:
            .. code-block:: python

                # Play local MP3
                await app.play_audio(chat_id, "music.mp3")

                # Play live radio stream URL
                await app.play_audio(chat_id, "https://live.stream/radio.aac")

                # Play Telegram message audio without downloading to disk
                await app.play_audio(chat_id, message.audio)
                await app.play_audio(chat_id, message)

                # Play Telegram Document (e.g. lossless FLAC)
                await app.play_audio(chat_id, message.document)

                # Play by Telegram file_id string
                await app.play_audio(chat_id, "CQACAgQAAx0CYg-qTQAB...")
        """
        return await self.calls.play(chat_id=chat_id, media=audio, video=False)