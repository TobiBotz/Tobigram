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


class AcceptUrlAuth:
    async def accept_url_auth(
        self: pyrogram.Client,
        url: str,
        write_allowed: bool | None = None,
        share_phone_number: bool | None = None,
        chat_id: int | str | None = None,
        message_id: int | None = None,
        button_id: int | None = None,
        match_code: str | None = None,
    ) -> raw.base.UrlAuthResult:
        """Accept URL authorization (login via Telegram for a website).

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            url (``str``):
                The URL to accept authorization for.

            write_allowed (``bool``, *optional*):
                If True, allow the bot to send messages.

            share_phone_number (``bool``, *optional*):
                If True, share your phone number with the bot.

            chat_id (``int`` | ``str``, *optional*):
                Chat containing the inline keyboard button.

            message_id (``int``, *optional*):
                The message with the button.

            button_id (``int``, *optional*):
                The button ID.

            match_code (``str``, *optional*):
                URL match code.

        Returns:
            :obj:`~pyrogram.raw.base.UrlAuthResult`: The URL auth result with the authorized URL.

        Example:
            .. code-block:: python

                result = await app.accept_url_auth(url="https://example.com", write_allowed=True)
        """
        peer = await self.resolve_peer(chat_id) if chat_id else None

        return await self.invoke(
            raw.functions.messages.AcceptUrlAuth(
                url=url,
                write_allowed=write_allowed,
                share_phone_number=share_phone_number,
                peer=peer,
                msg_id=message_id,
                button_id=button_id,
                match_code=match_code,
            )
        )
