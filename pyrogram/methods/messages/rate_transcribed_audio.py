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


class RateTranscribedAudio:
    async def rate_transcribed_audio(
        self: pyrogram.Client,
        chat_id: int | str,
        message_id: int,
        transcription_id: int,
        good: bool,
    ) -> bool:
        """Rate the quality of a transcribed audio message.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            message_id (``int``):
                The message ID of the transcribed audio.

            transcription_id (``int``):
                The transcription ID returned when transcribing.

            good (``bool``):
                Pass True if the transcription was accurate, False otherwise.

        Returns:
            ``bool``: True on success.

        Example:
            .. code-block:: python

                await app.rate_transcribed_audio(chat_id, message_id, transcription_id, good=True)
        """
        peer = await self.resolve_peer(chat_id)

        return await self.invoke(
            raw.functions.messages.RateTranscribedAudio(
                peer=peer,
                msg_id=message_id,
                transcription_id=transcription_id,
                good=good,
            )
        )
