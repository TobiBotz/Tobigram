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

from typing import Any

import pyrogram
from pyrogram import raw


class InvokeWithLayer:
    async def invoke_with_layer(
        self: pyrogram.Client,
        layer: int,
        query: raw.core.TLObject,
    ) -> Any:
        """Invoke the specified query using the specified API layer.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            layer (``int``):
                The API layer to use.

            query (Any function from :obj:`~pyrogram.raw.functions`):
                The query to invoke.

        Returns:
            Any object from :obj:`~pyrogram.raw.types`: On success, query result is returned.
        """
        return await self.invoke(
            raw.functions.InvokeWithLayer(
                layer=layer,
                query=query,
            )
        )
