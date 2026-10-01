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
from pyrogram import enums, raw, types

from ..object import Object


class ChatPhotoSticker(Object):
    """Information about the sticker, which was used to create the chat photo.
    The sticker is shown at the center of the photo and occupies at most 67% of it.

    Parameters:
        type (:obj:`~pyrogram.enums.ChatPhotoStickerType`):
            Type of the sticker.

        set_name (``str``, *optional*):
            Name of the sticker set to which the sticker belongs.

        sticker_id (``int``, *optional*):
            Identifier of the sticker in the set.

        custom_emoji_id (``str``, *optional*):
            Custom emoji id.
    """

    def __init__(
        self,
        *,
        client: pyrogram.Client | None = None,
        type: enums.ChatPhotoStickerType,
        set_name: str | None = None,
        sticker_id: int | None = None,
        custom_emoji_id: str | None = None,
    ):
        super().__init__(client)

        self.type = type
        self.set_name = set_name
        self.sticker_id = sticker_id
        self.custom_emoji_id = custom_emoji_id

    @staticmethod
    def _parse(
        client: pyrogram.Client | None,
        video_sizes: list[raw.base.VideoSize] | None,
    ) -> ChatPhotoSticker | None:
        if not isinstance(video_sizes, list):
            return None

        for video_size in video_sizes:
            if isinstance(video_size, raw.types.VideoSizeEmojiMarkup):
                return ChatPhotoSticker(
                    type=enums.ChatPhotoStickerType.CUSTOM_EMOJI,
                    custom_emoji_id=str(video_size.emoji_id),
                    client=client,
                )

            if isinstance(video_size, raw.types.VideoSizeStickerMarkup):
                sticker_set = video_size.stickerset
                set_name = None

                if isinstance(sticker_set, raw.types.InputStickerSetShortName):
                    set_name = sticker_set.short_name
                elif hasattr(sticker_set, "id") and hasattr(sticker_set, "access_hash"):
                    set_name = types.Sticker.cache.get((sticker_set.id, sticker_set.access_hash))
                    if not set_name:
                        set_name = str(sticker_set.id)
                elif hasattr(sticker_set, "id"):
                    set_name = str(sticker_set.id)

                return ChatPhotoSticker(
                    type=enums.ChatPhotoStickerType.REGULAR_OR_MASK,
                    set_name=set_name,
                    sticker_id=video_size.sticker_id,
                    client=client,
                )

        return None
