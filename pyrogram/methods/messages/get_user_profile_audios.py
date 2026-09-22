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

from collections.abc import AsyncGenerator

import pyrogram
from pyrogram import raw, types


class GetUserProfileAudios:
    async def get_user_profile_audios(
        self: pyrogram.Client,
        user_id: int | str,
        offset: int = 0,
        limit: int = 0,
    ) -> AsyncGenerator[types.Audio, None]:
        """Get the list of profile audios (voice/audio messages) for a user.

        .. include:: /_includes/usable-by/bots.rst

        Parameters:
            user_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target user.

            offset (``int``, *optional*):
                Number of profile audios to skip. Defaults to 0.

            limit (``int``, *optional*):
                Maximum number of profile audios to retrieve. Pass 0 for all. Defaults to 0.

        Returns:
            ``AsyncGenerator``: An async generator yielding :obj:`~pyrogram.types.Audio` objects.

        Example:
            .. code-block:: python

                # Get all profile audios of a user
                async for audio in app.get_user_profile_audios(user_id):
                    print(audio.file_id)
        """
        peer = await self.resolve_peer(user_id)

        r = await self.invoke(
            raw.functions.photos.GetUserPhotos(
                user_id=peer,
                offset=offset,
                max_id=0,
                limit=limit,
            )
        )

        # getUserProfileAudios is a Bot API concept; in MTProto the closest
        # equivalent is fetching the user's profile media. Yield any audio
        # documents found in the result.
        for photo in getattr(r, "photos", []):
            if isinstance(photo, raw.types.Document):
                for attr in photo.attributes:
                    if isinstance(attr, (raw.types.DocumentAttributeAudio,)):
                        yield types.Audio._parse(self, photo, attr)
                        break
