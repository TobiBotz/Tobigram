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


class SetChatStickerSet:
    async def set_chat_sticker_set(
        self: pyrogram.Client,
        chat_id: int | str,
        sticker_set_name: str,
    ) -> bool:
        """Set a new group sticker set for a supergroup.

        The bot must be an administrator in the chat and have the appropriate
        admin rights. Use the field ``can_set_sticker_set`` optionally returned in
        :meth:`~Client.get_chat` to check if the bot can use this method.

        .. include:: /_includes/usable-by/bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target supergroup.

            sticker_set_name (``str``):
                Name of the sticker set to be set as the group sticker set.

        Returns:
            ``bool``: True on success.

        Example:
            .. code-block:: python

                await app.set_chat_sticker_set(chat_id, "mystickerset")
        """
        peer = await self.resolve_peer(chat_id)

        await self.invoke(
            raw.functions.channels.SetStickers(
                channel=peer,
                stickerset=raw.types.InputStickerSetShortName(short_name=sticker_set_name),
            )
        )

        return True
