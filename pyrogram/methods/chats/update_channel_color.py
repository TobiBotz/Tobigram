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

# ***************************
# GENERATED FILE - DO NOT EDIT
# Source: tl:channels.updateColor
# ***************************

from typing import Union, Optional

import pyrogram
from pyrogram import raw
from pyrogram import types


class UpdateChannelColor:
    async def update_channel_color(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        for_profile: Optional[bool] = None,
        color: Optional[int] = None,
        background_emoji_id: Optional[int] = None,
    ) -> "types.Message":
        """Update the accent color of a channel.

        .. include:: /_includes/usable-by/users.rst

        Parameters:

            for_profile (bool): Whether to set the profile color instead


            color (int): New accent color ID


            background_emoji_id (int): Custom emoji ID for the background



        Returns:
            :obj:`~pyrogram.types.Message`

        Example:
            .. code-block:: python

                await app.update_channel_color(chat_id, ...)
        """

        r = await self.invoke(
            raw.functions.channels.updateColor(
                
                for_profile=for_profile,
                channel=await self.resolve_peer(chat_id),
                color=color,
                background_emoji_id=background_emoji_id,
            )
        )

        for i in r.updates:
            if isinstance(i, (raw.types.UpdateNewMessage,
                              raw.types.UpdateNewChannelMessage,
                              raw.types.UpdateNewScheduledMessage)):
                return await types.Message._parse(
                    self, i.message,
                    {i.id: i for i in r.users},
                    {i.id: i for i in r.chats},
                    is_scheduled=isinstance(i, raw.types.UpdateNewScheduledMessage)
                )
