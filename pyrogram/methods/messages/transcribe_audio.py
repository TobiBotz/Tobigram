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
from pyrogram import raw, types


class TranscribeAudio:
    async def transcribe_audio(
        self: pyrogram.Client,
        chat_id: int | str,
        message_id: int,
    ) -> types.TranscribedAudio:
        """Transcribe speech in a voice message or video note into text.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            message_id (``int``):
                Identifier of the message containing the voice note or video note.

        Returns:
            :obj:`~pyrogram.types.TranscribedAudio`: On success, the transcribed audio object is returned.

        Example:
            .. code-block:: python

                # Transcribe speech in a voice note
                transcription = await app.transcribe_audio(chat_id, message_id)
                print(transcription.text)
        """
        r = await self.invoke(
            raw.functions.messages.TranscribeAudio(
                peer=await self.resolve_peer(chat_id),
                msg_id=message_id,
            )
        )

        return types.TranscribedAudio._parse(self, r)
