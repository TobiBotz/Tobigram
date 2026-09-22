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


class ProlongWebView:
    async def prolong_web_view(
        self: pyrogram.Client,
        chat_id: int | str,
        bot_id: int | str,
        query_id: int,
        silent: bool | None = None,
        reply_to: raw.base.InputReplyTo | None = None,
        send_as: int | str | None = None,
    ) -> bool:
        """Prolong an open web app session to prevent it from expiring.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                The chat where the web app is open.

            bot_id (``int`` | ``str``):
                The bot that owns the web app.

            query_id (``int``):
                The web view query ID.

            silent (``bool``, *optional*):
                If True, send silently.

            reply_to (:obj:`~pyrogram.raw.base.InputReplyTo`, *optional*):
                Message to reply to.

            send_as (``int`` | ``str``, *optional*):
                Peer to send as.

        Returns:
            ``bool``: True on success.

        Example:
            .. code-block:: python

                await app.prolong_web_view(chat_id, bot_id, query_id=123)
        """
        peer = await self.resolve_peer(chat_id)
        bot = await self.resolve_peer(bot_id)
        send_as_peer = await self.resolve_peer(send_as) if send_as else None

        return await self.invoke(
            raw.functions.messages.ProlongWebView(
                peer=peer,
                bot=bot,
                query_id=query_id,
                silent=silent,
                reply_to=reply_to,
                send_as=send_as_peer,
            )
        )
