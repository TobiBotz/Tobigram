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


class RequestChatJoinWebView:
    async def request_chat_join_web_view(
        self: pyrogram.Client,
        query_id: int,
        theme_params: raw.base.DataJSON | None = None,
        platform: str = "android",
    ) -> raw.base.Updates:
        """Request joining a chat via a web view.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            query_id (``int``):
                The web view query ID.

            theme_params (:obj:`~pyrogram.raw.base.DataJSON`, *optional*):
                Theme parameters for the web view.

            platform (``str``, *optional*):
                Platform identifier. Defaults to "android".

        Returns:
            :obj:`~pyrogram.raw.base.Updates`: The updates object.

        Example:
            .. code-block:: python

                await app.request_chat_join_web_view(query_id=123)
        """
        return await self.invoke(
            raw.functions.messages.RequestChatJoinWebView(
                query_id=query_id,
                theme_params=theme_params,
                platform=platform,
            )
        )
