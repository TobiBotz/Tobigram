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

import pyrogram
from pyrogram import raw, types, utils
from pyrogram.file_id import (
    FileId,
    FileType,
    FileUniqueId,
    FileUniqueType,
    ThumbnailSource,
)

from ..object import Object

if TYPE_CHECKING:
    from datetime import datetime


class ChatPhoto(Object):
    """A chat photo.

    Parameters:
        small_file_id (``str``):
            File identifier of small (160x160) chat photo.
            This file_id can be used only for photo download and only for as long as the photo is not changed.

        small_photo_unique_id (``str``):
            Unique file identifier of small (160x160) chat photo, which is supposed to be the same over time and for
            different accounts. Can't be used to download or reuse the file.

        big_file_id (``str``):
            File identifier of big (640x640) chat photo.
            This file_id can be used only for photo download and only for as long as the photo is not changed.

        big_photo_unique_id (``str``):
            Unique file identifier of big (640x640) chat photo, which is supposed to be the same over time and for
            different accounts. Can't be used to download or reuse the file.

        has_animation (``bool``, *optional*):
            True, if animated profile picture is available for this user.

        is_personal (``bool``, *optional*):
            True, if the photo is visible only for the current user.

        added_date (:py:obj:`~datetime.datetime`, *optional*):
            Date when the photo was set.

        animation (:obj:`~pyrogram.types.AnimatedChatPhoto`, *optional*):
            Animated chat photo video details, if available.

        sticker (:obj:`~pyrogram.types.ChatPhotoSticker`, *optional*):
            Chat photo sticker or custom emoji details, if available.

        stripped_thumb (``bytes``, *optional*):
            Thumbnail image preview in bytes, if available.
    """

    def __init__(
        self,
        *,
        client: pyrogram.Client | None = None,
        small_file_id: str,
        small_photo_unique_id: str,
        big_file_id: str,
        big_photo_unique_id: str,
        has_animation: bool | None = None,
        is_personal: bool | None = None,
        added_date: datetime | None = None,
        animation: types.AnimatedChatPhoto | None = None,
        sticker: types.ChatPhotoSticker | None = None,
        stripped_thumb: bytes | None = None,
    ):
        super().__init__(client)

        self.small_file_id = small_file_id
        self.small_photo_unique_id = small_photo_unique_id
        self.big_file_id = big_file_id
        self.big_photo_unique_id = big_photo_unique_id
        self.has_animation = has_animation
        self.is_personal = is_personal
        self.added_date = added_date
        self.animation = animation
        self.sticker = sticker
        self.stripped_thumb = stripped_thumb

    @staticmethod
    def _parse(
        client: pyrogram.Client | None,
        chat_photo: raw.types.UserProfilePhoto | raw.types.ChatPhoto | raw.types.Photo,
        peer_id: int = 0,
        peer_access_hash: int = 0,
    ) -> ChatPhoto | None:
        if not isinstance(
            chat_photo, (raw.types.UserProfilePhoto, raw.types.ChatPhoto, raw.types.Photo)
        ):
            return None

        if peer_access_hash is None:
            return None

        photo_id = (
            chat_photo.photo_id
            if isinstance(chat_photo, (raw.types.UserProfilePhoto, raw.types.ChatPhoto))
            else chat_photo.id
        )

        added_date = (
            utils.timestamp_to_datetime(chat_photo.date)
            if getattr(chat_photo, "date", None)
            else None
        )

        animation = None
        sticker = None
        has_video = getattr(chat_photo, "has_video", None)

        if isinstance(chat_photo, raw.types.Photo) and getattr(chat_photo, "video_sizes", None):
            animation = types.AnimatedChatPhoto._parse(client, chat_photo)
            sticker = types.ChatPhotoSticker._parse(client, chat_photo.video_sizes)

        if has_video is not None:
            has_animation = bool(has_video)
        elif animation is not None or sticker is not None:
            has_animation = True
        else:
            has_animation = False

        return ChatPhoto(
            small_file_id=FileId(
                file_type=FileType.CHAT_PHOTO,
                dc_id=chat_photo.dc_id,
                media_id=photo_id,
                access_hash=0,
                volume_id=0,
                thumbnail_source=ThumbnailSource.CHAT_PHOTO_SMALL,
                local_id=0,
                chat_id=peer_id,
                chat_access_hash=peer_access_hash,
            ).encode(),
            small_photo_unique_id=FileUniqueId(
                file_unique_type=FileUniqueType.DOCUMENT, media_id=photo_id
            ).encode(),
            big_file_id=FileId(
                file_type=FileType.CHAT_PHOTO,
                dc_id=chat_photo.dc_id,
                media_id=photo_id,
                access_hash=0,
                volume_id=0,
                thumbnail_source=ThumbnailSource.CHAT_PHOTO_BIG,
                local_id=0,
                chat_id=peer_id,
                chat_access_hash=peer_access_hash,
            ).encode(),
            big_photo_unique_id=FileUniqueId(
                file_unique_type=FileUniqueType.DOCUMENT, media_id=photo_id
            ).encode(),
            has_animation=has_animation,
            is_personal=getattr(chat_photo, "personal", False) or False,
            added_date=added_date,
            animation=animation,
            sticker=sticker,
            stripped_thumb=getattr(chat_photo, "stripped_thumb", None),
            client=client,
        )
