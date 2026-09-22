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


class UploadContactProfilePhoto:
    async def upload_contact_profile_photo(
        self: pyrogram.Client,
        user_id: int | str,
        *,
        photo: raw.base.InputFile | None = None,
        video: raw.base.InputFile | None = None,
        video_start_ts: float | None = None,
        video_emoji_markup: raw.base.VideoSize | None = None,
        suggest: bool | None = None,
        save: bool | None = None,
    ) -> raw.base.photos.Photo:
        """Upload a custom profile picture for a contact, or suggest a new profile picture to a contact.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            user_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target contact.

            photo (:obj:`~pyrogram.raw.base.InputFile`, *optional*):
                Profile photo to set or suggest.

            video (:obj:`~pyrogram.raw.base.InputFile`, *optional*):
                Animated profile picture video.

            video_start_ts (``float``, *optional*):
                Floating point UNIX timestamp in seconds for preview frame.

            video_emoji_markup (:obj:`~pyrogram.raw.base.VideoSize`, *optional*):
                Animated sticker profile picture markup.

            suggest (``bool``, *optional*):
                If set, sends a suggest profile photo service message to the user.

            save (``bool``, *optional*):
                If set, removes a previously set personal profile picture.

        Returns:
            :obj:`~pyrogram.raw.base.photos.Photo`: The photo object.

        Example:
            .. code-block:: python

                await app.upload_contact_profile_photo(user_id, photo=input_file)
        """
        return await self.invoke(
            raw.functions.photos.UploadContactProfilePhoto(
                user_id=utils.get_input_user(await self.resolve_peer(user_id)),
                file=photo,
                video=video,
                video_start_ts=video_start_ts,
                video_emoji_markup=video_emoji_markup,
                suggest=suggest,
                save=save,
            )
        )
