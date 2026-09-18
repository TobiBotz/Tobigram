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


import pyrogram
from pyrogram import raw, utils


class SetChatAccentColor:
    async def set_chat_accent_color(
        self: "pyrogram.Client",
        chat_id: int | str,
        accent_color_id: int | None = None,
        background_custom_emoji_id: int | None = None,
        for_profile: bool | None = None,
    ) -> bool:
        """Change the accent color of your account or of a channel.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                Pass "me" or "self" to change the color of your own account.

            accent_color_id (``int``, *optional*):
                Identifier of the accent color to use.
                Pass None to remove the current color.

            background_custom_emoji_id (``int``, *optional*):
                Identifier of the custom emoji shown in the profile or the message background.

            for_profile (``bool``, *optional*):
                Pass True to change the profile color instead of the message accent color.

        Returns:
            ``bool``: On success, True is returned.

        Raises:
            ValueError: In case the chat is neither your own account nor a channel.

        Example:
            .. code-block:: python

                await app.set_chat_accent_color("me", 5)
        """

        peer = await self.resolve_peer(chat_id)

        if isinstance(peer, raw.types.InputPeerSelf):
            has_color = accent_color_id is not None or background_custom_emoji_id is not None

            r = await self.invoke(
                raw.functions.account.UpdateColor(
                    for_profile=for_profile,
                    color=raw.types.PeerColor(
                        color=accent_color_id, background_emoji_id=background_custom_emoji_id
                    )
                    if has_color
                    else None,
                )
            )
        elif isinstance(peer, (raw.types.InputPeerChannel, raw.types.InputPeerChannelFromMessage)):
            r = await self.invoke(
                raw.functions.channels.UpdateColor(
                    channel=utils.get_input_channel(peer),
                    for_profile=for_profile,
                    color=accent_color_id,
                    background_emoji_id=background_custom_emoji_id,
                )
            )
        else:
            raise ValueError("The chat_id must be your own account or a channel")

        return bool(r)
