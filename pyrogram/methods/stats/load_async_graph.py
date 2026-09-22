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


class LoadAsyncGraph:
    async def load_async_graph(
        self: pyrogram.Client,
        token: str,
        x: int | None = None,
    ) -> raw.base.StatsGraph:
        """Load channel statistics graph asynchronously.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            token (``str``):
                Graph token from statsGraphAsync constructor.

            x (``int``, *optional*):
                Zoom value, if required.

        Returns:
            :obj:`~pyrogram.raw.base.StatsGraph`: The loaded statistics graph.

        Example:
            .. code-block:: python

                graph = await app.load_async_graph(token)
        """
        return await self.invoke(
            raw.functions.stats.LoadAsyncGraph(
                token=token,
                x=x,
            )
        )
