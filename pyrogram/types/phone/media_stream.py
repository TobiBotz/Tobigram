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

from pyrogram.types.object import Object


class MediaStream(Object):
    """Audio or Video media stream descriptor for Voice Chats.

    Parameters:
        path (``str``):
            Local file path or remote stream URL (e.g. HTTP, HLS, RTMP, YouTube).

        video (``bool`` | ``str``, *optional*):
            Whether to stream video along with audio, or a specific video path.
            Defaults to False (audio only).

        volume (``int``, *optional*):
            Initial stream volume in percentage (0 to 200). Defaults to 100.

        bitrate (``int``, *optional*):
            Audio bitrate in kbps (e.g. 48, 64, 128). Defaults to 48.

        headers (``dict``, *optional*):
            Custom HTTP headers for remote stream fetch.
    """

    def __init__(
        self,
        path: str,
        video: bool | str = False,
        volume: int = 100,
        bitrate: int = 48,
        headers: dict | None = None,
    ):
        super().__init__()
        self.path = str(path)
        self.video = video
        self.volume = max(0, min(volume, 200))
        self.bitrate = bitrate
        self.headers = headers or {}

    @property
    def has_video(self) -> bool:
        """True if this media stream includes video."""
        return bool(self.video)
