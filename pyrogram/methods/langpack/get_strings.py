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


class GetStrings:
    async def get_strings(
        self: pyrogram.Client,
        lang_pack: str,
        lang_code: str,
        keys: list[str],
    ) -> list[raw.base.LangPackString]:
        """Get strings from a language pack.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            lang_pack (``str``):
                Platform identifier (i.e. ``android``, ``tdesktop``, etc).

            lang_code (``str``):
                Either an ISO 639-1 language code or a language pack name.

            keys (List of ``str``):
                Strings keys to get.

        Returns:
            List of :obj:`~pyrogram.raw.base.LangPackString`: List of language pack strings.

        Example:
            .. code-block:: python

                strings = await app.get_strings("android", "en", ["key1", "key2"])
        """
        return await self.invoke(
            raw.functions.langpack.GetStrings(
                lang_pack=lang_pack,
                lang_code=lang_code,
                keys=keys,
            )
        )
