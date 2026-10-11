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


class PerformApiRequest:
    async def perform_api_request(
        self: pyrogram.Client,
        endpoint: str,
        *,
        query: str | None = None,
        payload: str | None = None,
        post: bool | None = None,
    ) -> raw.base.toncenter.ApiResponse:
        """Execute a request against the Toncenter API endpoint.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            endpoint (``str``):
                The Toncenter endpoint to call.

            query (``str``, *optional*):
                Query string parameters.

            payload (``str``, *optional*):
                Request payload data.

            post (``bool``, *optional*):
                Whether to issue a POST request instead of GET.

        Returns:
            :obj:`~pyrogram.raw.base.toncenter.ApiResponse`: The response returned by the Toncenter API.

        Example:
            .. code-block:: python

                response = await app.perform_api_request(endpoint="getAddressInformation", query="address=EQ...")
        """
        return await self.invoke(
            raw.functions.toncenter.PerformApiRequest(
                endpoint=endpoint,
                query=query,
                payload=payload,
                post=post,
            )
        )
