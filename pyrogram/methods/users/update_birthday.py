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

from typing import Optional
import pyrogram
from pyrogram import raw


class UpdateBirthday:
    async def update_birthday(
        self: "pyrogram.Client",
        day: Optional[int] = None,
        month: Optional[int] = None,
        year: Optional[int] = None
    ) -> bool:
        """Update birthday in your profile.

        Calling it with no arguments removes the birthday from your profile.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            day (``int``, *optional*):
                Birthday day. Required together with *month* when setting a birthday.

            month (``int``, *optional*):
                Birthday month. Required together with *day* when setting a birthday.

            year (``int``, *optional*):
                Birthday year.

        Returns:
            ``bool``: True on success.

        Raises:
            ValueError: If only some of the arguments are given.

        Example:
            .. code-block:: python

                # Update your birthday
                await app.update_birthday(day=1, month=1, year=2000)

                # Remove birthday from profile
                await app.update_birthday()
        """
        birthday = None

        if day is not None and month is not None:
            birthday = raw.types.Birthday(day=day, month=month, year=year)
        elif (day, month, year) != (None, None, None):
            raise ValueError("Both day and month are required to set a birthday; pass no arguments to remove it")

        return bool(
            await self.invoke(
                raw.functions.account.UpdateBirthday(
                    birthday=birthday
                )
            )
        )

