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


class CreateConferenceCall:
    async def create_conference_call(
        self: pyrogram.Client,
        params: str | raw.base.DataJSON,
        random_id: int | None = None,
        muted: bool | None = None,
        video_stopped: bool | None = None,
        join: bool | None = None,
        public_key: int | None = None,
        block: bytes | None = None,
    ) -> raw.base.Updates:
        """Create and optionally join a new end-to-end encrypted conference call.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            params (``str`` | :obj:`~pyrogram.raw.base.DataJSON`):
                Signaling parameters payload JSON string or DataJSON object.

            random_id (``int``, *optional*):
                Unique client random ID for deduplication. Defaults to a random integer.

            muted (``bool``, *optional*):
                Pass True to mute microphone when joining.

            video_stopped (``bool``, *optional*):
                Pass True to disable video stream when joining.

            join (``bool``, *optional*):
                Pass True to also join the call, otherwise only create the link.

            public_key (``int``, *optional*):
                Fresh E2E public key for the creator.

            block (``bytes``, *optional*):
                Initial main-chain block for subchain 0.

        Returns:
            :obj:`~pyrogram.raw.base.Updates`: Updates resulting from creating the conference call.

        Example:
            .. code-block:: python

                await app.create_conference_call(params='{}', join=True)
        """
        if isinstance(params, str):
            params = raw.types.DataJSON(data=params)

        return await self.invoke(
            raw.functions.phone.CreateConferenceCall(
                params=params,
                random_id=random_id if random_id is not None else self.rnd_id(),
                muted=muted,
                video_stopped=video_stopped,
                join=join,
                public_key=public_key,
                block=block,
            )
        )
