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


class GetLanguages:
    async def get_languages(
        self: pyrogram.Client,
        lang_pack: str,
    ) -> list[raw.base.LangPackLanguage]:
        """Get information about all languages in a localization pack.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            lang_pack (``str``):
                Platform identifier (i.e. ``android``, ``tdesktop``, etc).

        Returns:
            List of :obj:`~pyrogram.raw.base.LangPackLanguage`: List of languages.

        Example:
            .. code-block:: python

                langs = await app.get_languages("android")
        """
        return await self.invoke(
            raw.functions.langpack.GetLanguages(
                lang_pack=lang_pack,
            )
        )
