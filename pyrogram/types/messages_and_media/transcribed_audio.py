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
from pyrogram import raw, utils

from ..object import Object
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime


class TranscribedAudio(Object):
    """Contains transcribed text from a voice message or video note.

    Parameters:
        transcription_id (``int``):
            Unique identifier of the transcription.

        text (``str``):
            Transcribed text.

        pending (``bool``, *optional*):
            True, if the transcription is still in progress and more text may follow.

        trial_remains_num (``int``, *optional*):
            For non-Premium users, remaining free transcriptions in the current trial period.

        trial_remains_until_date (:py:obj:`~datetime.datetime`, *optional*):
            For non-Premium users, date when the trial counter will reset.
    """

    def __init__(
        self,
        *,
        client: pyrogram.Client | None = None,
        transcription_id: int,
        text: str,
        pending: bool = False,
        trial_remains_num: int | None = None,
        trial_remains_until_date: datetime | None = None,
    ):
        super().__init__(client)

        self.transcription_id = transcription_id
        self.text = text
        self.pending = pending
        self.trial_remains_num = trial_remains_num
        self.trial_remains_until_date = trial_remains_until_date

    @staticmethod
    def _parse(
        client: pyrogram.Client,
        transcribed_audio: raw.types.messages.TranscribedAudio,
    ) -> TranscribedAudio:
        return TranscribedAudio(
            client=client,
            transcription_id=transcribed_audio.transcription_id,
            text=transcribed_audio.text,
            pending=getattr(transcribed_audio, "pending", False) or False,
            trial_remains_num=getattr(transcribed_audio, "trial_remains_num", None),
            trial_remains_until_date=utils.timestamp_to_datetime(
                getattr(transcribed_audio, "trial_remains_until_date", None)
            ),
        )
