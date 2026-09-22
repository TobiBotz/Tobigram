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


class UpdateStarRefProgram:
    async def update_star_ref_program(
        self: pyrogram.Client,
        bot: int | str,
        commission_permille: int,
        duration_months: int | None = None,
    ) -> raw.base.StarRefProgram:
        """Create, edit or delete the affiliate program of a bot we own.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            bot (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target bot.

            commission_permille (``int``):
                The permille commission rate (e.g. 100 for 10%). Can be 0 to terminate the affiliate program.

            duration_months (``int``, *optional*):
                Indicates the duration of the affiliate program in months; if not set, there is no expiration date.

        Returns:
            :obj:`~pyrogram.raw.base.StarRefProgram`: The affiliate program details.

        Example:
            .. code-block:: python

                program = await app.update_star_ref_program("my_bot", commission_permille=50)
        """
        return await self.invoke(
            raw.functions.bots.UpdateStarRefProgram(
                bot=await self.resolve_peer(bot),
                commission_permille=commission_permille,
                duration_months=duration_months,
            )
        )
