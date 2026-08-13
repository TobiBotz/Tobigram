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

from datetime import datetime
from typing import Optional, Union

import pyrogram
from pyrogram import raw, utils

MUTE_FOREVER = 2147483647


class UpdateChatNotifications:
    async def update_chat_notifications(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        mute: Optional[bool] = None,
        mute_until: Optional[datetime] = None,
        show_previews: Optional[bool] = None
    ) -> bool:
        """Update the notification settings of a chat.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            mute (``bool``, *optional*):
                Pass True to mute the chat, False to unmute it.

            mute_until (:py:obj:`~datetime.datetime`, *optional*):
                Date when the chat will be unmuted. Defaults to forever.
                Only used when *mute* is True.

            show_previews (``bool``, *optional*):
                Pass True to show message previews in notifications, False to hide them.

        Returns:
            ``bool``: On success, True is returned.

        Example:
            .. code-block:: python

                # Mute a chat forever
                await app.update_chat_notifications(chat_id, mute=True)

                # Unmute a chat
                await app.update_chat_notifications(chat_id, mute=False)
        """

        if mute is None:
            mute_until_ts = None
        elif not mute:
            mute_until_ts = 0
        else:
            mute_until_ts = utils.datetime_to_timestamp(mute_until) or MUTE_FOREVER

        return await self.invoke(
            raw.functions.account.UpdateNotifySettings(
                peer=raw.types.InputNotifyPeer(
                    peer=await self.resolve_peer(chat_id)
                ),
                settings=raw.types.InputPeerNotifySettings(
                    show_previews=show_previews,
                    mute_until=mute_until_ts
                )
            )
        )
