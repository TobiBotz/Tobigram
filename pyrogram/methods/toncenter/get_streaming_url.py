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


class GetStreamingUrl:
    async def get_streaming_url(
        self: pyrogram.Client,
    ) -> raw.base.toncenter.StreamingUrl:
        """Obtain a streaming URL for real-time Toncenter updates.

        .. include:: /_includes/usable-by/users.rst

        Returns:
            :obj:`~pyrogram.raw.base.toncenter.StreamingUrl`: Streaming endpoint URL for Toncenter updates.

        Example:
            .. code-block:: python

                url_info = await app.get_streaming_url()
        """
        return await self.invoke(raw.functions.toncenter.GetStreamingUrl())
