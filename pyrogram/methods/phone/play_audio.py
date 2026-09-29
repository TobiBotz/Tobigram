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


class PlayAudio:
    async def play_audio(
        self: pyrogram.Client,
        chat_id: int | str,
        audio: str | types.MediaStream,
    ) -> types.GroupCall:
        """Stream an audio file or remote live URL into group voice chat.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            audio (``str`` | :obj:`~pyrogram.types.MediaStream`):
                Path to the audio file, live stream URL, or a MediaStream descriptor.

        Returns:
            :obj:`~pyrogram.types.GroupCall`: On success, group call information is returned.

        Example:
            .. code-block:: python

                # Play local MP3
                await app.play_audio(chat_id, "music.mp3")

                # Play live radio stream URL
                await app.play_audio(chat_id, "https://live.stream/radio.aac")
        """
        if isinstance(audio, str):
            media = types.MediaStream(path=audio)
        else:
            media = audio

        return await self.calls.play(chat_id=chat_id, media=media)

    play = play_audio
