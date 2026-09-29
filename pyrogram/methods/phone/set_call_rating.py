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


class SetCallRating:
    async def set_call_rating(
        self: pyrogram.Client,
        call_id: int,
        access_hash: int,
        rating: int,
        comment: str = "",
        user_initiative: bool | None = None,
    ) -> raw.base.Updates:
        """Send quality rating and feedback for a finished phone call.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            call_id (``int``):
                The unique phone call ID.

            access_hash (``int``):
                The access hash of the phone call.

            rating (``int``):
                Call rating from 1 to 5 stars.

            comment (``str``, *optional*):
                Comment or problem description. Defaults to empty string.

            user_initiative (``bool``, *optional*):
                Pass True if the rating is initiated by the user rather than requested by Telegram.

        Returns:
            :obj:`~pyrogram.raw.base.Updates`: Updates resulting from the rating submission.

        Example:
            .. code-block:: python

                await app.set_call_rating(call_id=123, access_hash=456, rating=5, comment="Great call quality!")
        """
        return await self.invoke(
            raw.functions.phone.SetCallRating(
                peer=raw.types.InputPhoneCall(id=call_id, access_hash=access_hash),
                rating=rating,
                comment=comment,
                user_initiative=user_initiative,
            )
        )
