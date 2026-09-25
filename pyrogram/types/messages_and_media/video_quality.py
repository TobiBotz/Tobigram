# Pyrogram - Telegram MTProto API Client Library for Python
# Copyright (C) 2017-present Dan <https://github.com/delivrance>
#
# This file is part of Pyrogram.
#
# Pyrogram is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Pyrogram is distributed in the hope that it will be useful,
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Pyrogram.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import annotations

from pyrogram.file_id import FileId, FileType, FileUniqueId, FileUniqueType
from pyrogram.types.object import Object
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pyrogram import raw
    import pyrogram


class VideoQuality(Object):
    """This object represents a video file of a specific quality.

    Parameters:
        file_id (``str``):
            Identifier for this file, which can be used to download or reuse the file.

        file_unique_id (``str``):
            Unique identifier for this file, which is supposed to be the same over time and for different accounts.
            Can't be used to download or reuse the file.

        width (``int``):
            Video width as defined by sender.

        height (``int``):
            Video height as defined by sender.

        codec (``str``):
            Codec used for video file encoding, for example, "h264", "h265", or "av1".

        file_size (``int``, *optional*):
            File size.
    """

    def __init__(
        self,
        *,
        client: pyrogram.Client | None = None,
        file_id: str,
        file_unique_id: str,
        width: int,
        height: int,
        codec: str,
        file_size: int | None = None,
    ):
        super().__init__(client)

        self.file_id = file_id
        self.file_unique_id = file_unique_id
        self.width = width
        self.height = height
        self.codec = codec
        self.file_size = file_size

    @staticmethod
    def _parse(
        client: pyrogram.Client,
        doc: raw.types.Document,
        video_attributes: raw.types.DocumentAttributeVideo,
    ) -> VideoQuality:
        return VideoQuality(
            file_id=FileId(
                file_type=FileType.VIDEO,
                dc_id=doc.dc_id,
                media_id=doc.id,
                access_hash=doc.access_hash,
                file_reference=doc.file_reference,
            ).encode(),
            file_unique_id=FileUniqueId(
                file_unique_type=FileUniqueType.DOCUMENT, media_id=doc.id
            ).encode(),
            width=getattr(video_attributes, "w", None),
            height=getattr(video_attributes, "h", None),
            codec=getattr(video_attributes, "video_codec", None),
            file_size=doc.size,
            client=client,
        )
