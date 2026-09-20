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
from pyrogram import raw, types


class StartBot:
    async def start_bot(
        self: pyrogram.Client,
        chat_id: int | str,
        param: str = "",
    ) -> types.Message | None:
        """Start a bot, optionally passing a deep linking parameter.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the bot you want to start.

            param (``str``, *optional*):
                Text of the deep linking parameter (up to 64 characters).
                Defaults to "" (empty string), which sends a plain "/start".

        Returns:
            :obj:`~pyrogram.types.Message` | ``None``: On success, the sent message is returned,
            otherwise, in case the server answered with no message, None is returned.

        Example:
            .. code-block:: python

                # Start a bot
                await app.start_bot("tobigrambot")

                # Start a bot with a deep linking parameter
                await app.start_bot("tobigrambot", "ref123456")
        """

        if not param:
            return await self.send_message(chat_id, "/start")

        peer = await self.resolve_peer(chat_id)

        r = await self.invoke(
            raw.functions.messages.StartBot(
                bot=peer,
                peer=peer,
                random_id=self.rnd_id(),
                start_param=param,
            )
        )

        users = {i.id: i for i in r.users}
        chats = {i.id: i for i in r.chats}

        for i in r.updates:
            if isinstance(
                i,
                (raw.types.UpdateNewMessage, raw.types.UpdateNewChannelMessage),
            ):
                return await types.Message._parse(self, i.message, users, chats)

        return None
