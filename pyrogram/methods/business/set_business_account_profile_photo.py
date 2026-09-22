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

from typing import BinaryIO

import pyrogram
from pyrogram import raw


class SetBusinessAccountProfilePhoto:
    async def set_business_account_profile_photo(
        self: pyrogram.Client,
        business_connection_id: str,
        photo: str | BinaryIO,
        is_public: bool | None = None,
    ) -> bool:
        """Change the profile photo of a managed business account.

        Requires the ``can_edit_profile_photo`` business bot right.

        .. include:: /_includes/usable-by/bots.rst

        Parameters:
            business_connection_id (``str``):
                Unique identifier of the business connection.

            photo (``str`` | ``BinaryIO``):
                New profile photo. Pass a file path as string to upload a local file,
                or pass a file-like object (BinaryIO).

            is_public (``bool``, *optional*):
                Pass True to set the public photo (visible to everyone even if the main photo is hidden by privacy settings).

        Returns:
            ``bool``: True on success.

        Example:
            .. code-block:: python

                await app.set_business_account_profile_photo(connection_id, "photo.jpg")
        """
        if isinstance(photo, str):
            with open(photo, "rb") as f:
                uploaded = await self.save_file(f)
        else:
            uploaded = await self.save_file(photo)

        await self.invoke(
            raw.functions.photos.UploadProfilePhoto(
                file=uploaded,
                video=None,
                fallback=is_public,
            ),
            business_connection_id=business_connection_id,
        )

        return True
