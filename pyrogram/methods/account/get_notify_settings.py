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


class GetNotifySettings:
    async def get_notify_settings(
        self: pyrogram.Client,
        peer: raw.base.InputNotifyPeer,
    ) -> raw.base.PeerNotifySettings:
        """Gets current notification settings for a given user/group, or all users/all groups.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            peer (:obj:`~pyrogram.raw.base.InputNotifyPeer`):
                Notification source.

        Returns:
            :obj:`~pyrogram.raw.base.PeerNotifySettings`: On success, notification settings are returned.
        """
        return await self.invoke(
            raw.functions.account.GetNotifySettings(
                peer=peer,
            )
        )
