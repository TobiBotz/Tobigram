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

from pyrogram import enums
from ..update import Update

if TYPE_CHECKING:
    import pyrogram


class StreamEnded(Update):
    """An audio or video stream has finished playing in a voice chat.

    Parameters:
        chat_id (``int``):
            Target chat identifier.

        stream_type (:obj:`~pyrogram.enums.StreamType` | ``str``, *optional*):
            Type of stream that ended (:obj:`~pyrogram.enums.StreamType.AUDIO` or :obj:`~pyrogram.enums.StreamType.VIDEO`).
    """

    def __init__(
        self,
        *,
        client: pyrogram.Client = None,
        chat_id: int,
        stream_type: enums.StreamType | str = enums.StreamType.AUDIO,
    ):
        super().__init__()
        self._client = client
        self.chat_id = chat_id
        self.stream_type = stream_type
