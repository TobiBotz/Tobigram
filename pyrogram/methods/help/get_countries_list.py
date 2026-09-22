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


class GetCountriesList:
    async def get_countries_list(
        self: pyrogram.Client,
        lang_code: str = "",
        hash: int = 0,
    ) -> raw.base.help.CountriesList:
        """Get the list of supported countries.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            lang_code (``str``, *optional*):
                Language code for country names. Defaults to empty string.

            hash (``int``, *optional*):
                Hash for caching. Defaults to 0.

        Returns:
            :obj:`~pyrogram.raw.base.help.CountriesList`: The countries list.

        Example:
            .. code-block:: python

                countries = await app.get_countries_list()
        """
        return await self.invoke(
            raw.functions.help.GetCountriesList(
                lang_code=lang_code,
                hash=hash,
            )
        )
