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


class GetCollectibleInfo:
    async def get_collectible_info(
        self: pyrogram.Client,
        collectible: raw.base.InputCollectible | str,
    ) -> raw.base.fragment.CollectibleInfo:
        """Fetch information about a Fragment collectible (username or phone number).

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            collectible (:obj:`~pyrogram.raw.base.InputCollectible` | ``str``):
                The collectible to fetch info about. Can be an InputCollectible instance,
                a collectible username (e.g. "@durov" or "durov"), or a phone number (e.g. "+88812345678").

        Returns:
            :obj:`~pyrogram.raw.base.fragment.CollectibleInfo`: The collectible info.

        Example:
            .. code-block:: python

                info = await app.get_collectible_info("username")
        """
        if isinstance(collectible, str):
            c = collectible.strip()
            if c.startswith("+") or (c.isdigit() and len(c) > 5):
                collectible = raw.types.InputCollectiblePhone(phone=c.lstrip("+"))
            else:
                collectible = raw.types.InputCollectibleUsername(username=c.lstrip("@"))

        return await self.invoke(
            raw.functions.fragment.GetCollectibleInfo(
                collectible=collectible,
            )
        )
