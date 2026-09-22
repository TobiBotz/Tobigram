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


class RemoveBusinessAccountProfilePhoto:
    async def remove_business_account_profile_photo(
        self: pyrogram.Client,
        business_connection_id: str,
        is_public: bool | None = None,
    ) -> bool:
        """Remove the current profile photo of a managed business account.

        Requires the ``can_edit_profile_photo`` business bot right.

        .. include:: /_includes/usable-by/bots.rst

        Parameters:
            business_connection_id (``str``):
                Unique identifier of the business connection.

            is_public (``bool``, *optional*):
                Pass True to remove the public photo; pass False (default) to remove the main photo.

        Returns:
            ``bool``: True on success.

        Example:
            .. code-block:: python

                await app.remove_business_account_profile_photo(connection_id)
        """
        # Fetch the current profile photos and delete the most recent one
        r = await self.invoke(
            raw.functions.photos.GetUserPhotos(
                user_id=raw.types.InputUserSelf(),
                offset=0,
                max_id=0,
                limit=1,
            ),
            business_connection_id=business_connection_id,
        )

        if r.photos:
            await self.invoke(
                raw.functions.photos.DeletePhotos(
                    id=[
                        raw.types.InputPhoto(
                            id=r.photos[0].id,
                            access_hash=r.photos[0].access_hash,
                            file_reference=r.photos[0].file_reference,
                        )
                    ]
                ),
                business_connection_id=business_connection_id,
            )

        return True
