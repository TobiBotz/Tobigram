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


class RequestUrlAuth:
    async def request_url_auth(
        self: pyrogram.Client,
        url: str,
        chat_id: int | str | None = None,
        message_id: int | None = None,
        button_id: int | None = None,
        in_app_origin: str | None = None,
    ) -> raw.base.UrlAuthResult:
        """Request URL authorization for a login button or link preview.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            url (``str``):
                The URL to authorize.

            chat_id (``int`` | ``str``, *optional*):
                Chat containing the inline keyboard with the URL auth button.

            message_id (``int``, *optional*):
                The message with the button.

            button_id (``int``, *optional*):
                The button ID.

            in_app_origin (``str``, *optional*):
                Origin for in-app browser.

        Returns:
            :obj:`~pyrogram.raw.base.UrlAuthResult`: The URL auth result.

        Example:
            .. code-block:: python

                result = await app.request_url_auth(url="https://example.com")
        """
        peer = await self.resolve_peer(chat_id) if chat_id else None

        return await self.invoke(
            raw.functions.messages.RequestUrlAuth(
                url=url,
                peer=peer,
                msg_id=message_id,
                button_id=button_id,
                in_app_origin=in_app_origin,
            )
        )
