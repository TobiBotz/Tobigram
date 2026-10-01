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

from pyrogram import raw, types

from ..object import Object

if TYPE_CHECKING:
    import pyrogram


class AnimatedChatPhoto(Object):
    """An animated chat photo.

    Parameters:
        length (``int``):
            Length (width/height) of the animated photo frame.

        animation (:obj:`~pyrogram.types.Animation`):
            Animation video file.
    """

    def __init__(
        self,
        *,
        client: pyrogram.Client | None = None,
        length: int,
        animation: types.Animation,
    ):
        super().__init__(client)

        self.length = length
        self.animation = animation

    @staticmethod
    def _parse(
        client: pyrogram.Client | None,
        photo: raw.types.Photo,
        file_name: str | None = None,
    ) -> AnimatedChatPhoto | None:
        if not isinstance(photo, raw.types.Photo) or not getattr(photo, "video_sizes", None):
            return None

        video_sizes = [v for v in photo.video_sizes if isinstance(v, raw.types.VideoSize)]
        if not video_sizes:
            return None

        video_sizes.sort(key=lambda v: getattr(v, "w", 0) * getattr(v, "h", 0))
        main = video_sizes[-1]

        anim = types.Animation._parse_chat_animation(
            client, photo, file_name or f"video_{photo.date}.mp4"
        )
        if anim is None:
            return None

        return AnimatedChatPhoto(
            length=max(getattr(main, "w", 0), getattr(main, "h", 0)),
            animation=anim,
            client=client,
        )
