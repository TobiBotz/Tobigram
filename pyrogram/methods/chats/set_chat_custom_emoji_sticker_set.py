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


class SetChatCustomEmojiStickerSet:
    async def set_chat_custom_emoji_sticker_set(
        self: pyrogram.Client,
        chat_id: int | str,
        sticker_set_name: str | None = None,
    ) -> bool:
        """Set or remove the custom emoji sticker set for a supergroup.

        Only usable after reaching the required boost level.

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target supergroup.

            sticker_set_name (``str``, *optional*):
                Name of the custom emoji sticker set to set.
                Pass None to remove the custom emoji sticker set.
                Defaults to None.

        Returns:
            ``bool``: True on success.

        Example:
            .. code-block:: python

                # Set custom emoji set
                await app.set_chat_custom_emoji_sticker_set(chat_id, "mycustomemojis")

                # Remove custom emoji set
                await app.set_chat_custom_emoji_sticker_set(chat_id)
        """
        peer = await self.resolve_peer(chat_id)

        if sticker_set_name:
            stickerset = raw.types.InputStickerSetShortName(short_name=sticker_set_name)
        else:
            stickerset = raw.types.InputStickerSetEmpty()

        return await self.invoke(
            raw.functions.channels.SetEmojiStickers(
                channel=peer,
                stickerset=stickerset,
            )
        )
