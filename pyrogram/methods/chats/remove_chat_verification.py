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


class RemoveChatVerification:
    async def remove_chat_verification(
        self: pyrogram.Client,
        chat_id: int | str,
    ) -> bool:
        """Remove verification from a chat currently verified on behalf of the organization.

        The bot must have the ``can_verify_chats`` right to use this method.

        .. include:: /_includes/usable-by/bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target supergroup or channel.

        Returns:
            ``bool``: True on success.

        Example:
            .. code-block:: python

                await app.remove_chat_verification(chat_id)
        """
        peer = await self.resolve_peer(chat_id)

        await self.invoke(
            raw.functions.bots.SetCustomVerification(
                peer=peer,
                enabled=False,
            )
        )

        return True
