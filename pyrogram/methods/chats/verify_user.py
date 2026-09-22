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


class VerifyUser:
    async def verify_user(
        self: pyrogram.Client,
        user_id: int | str,
        custom_description: str | None = None,
    ) -> bool:
        """Verify a user on behalf of the organization represented by the bot.

        The bot must have the ``can_verify_users`` right to use this method.

        .. include:: /_includes/usable-by/bots.rst

        Parameters:
            user_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target user.

            custom_description (``str``, *optional*):
                Custom description for the verification badge shown on the user's profile.
                If not provided, the default organization description is used.
                The length limit is given by ``bot_verification_description_length_limit``.

        Returns:
            ``bool``: True on success.

        Example:
            .. code-block:: python

                # Verify a user with default description
                await app.verify_user(user_id)

                # Verify a user with a custom badge description
                await app.verify_user(user_id, custom_description="Verified partner")
        """
        peer = await self.resolve_peer(user_id)

        await self.invoke(
            raw.functions.bots.SetCustomVerification(
                peer=peer,
                enabled=True,
                custom_description=custom_description,
            )
        )

        return True
