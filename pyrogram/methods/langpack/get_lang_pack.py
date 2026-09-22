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


class GetLangPack:
    async def get_lang_pack(
        self: pyrogram.Client,
        lang_pack: str,
        lang_code: str,
    ) -> raw.base.LangPackDifference:
        """Get localization pack strings.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            lang_pack (``str``):
                Platform identifier (i.e. ``android``, ``tdesktop``, etc).

            lang_code (``str``):
                Either an ISO 639-1 language code or a language pack name.

        Returns:
            :obj:`~pyrogram.raw.base.LangPackDifference`: The language pack strings.

        Example:
            .. code-block:: python

                pack = await app.get_lang_pack("android", "en")
        """
        return await self.invoke(
            raw.functions.langpack.GetLangPack(
                lang_pack=lang_pack,
                lang_code=lang_code,
            )
        )
