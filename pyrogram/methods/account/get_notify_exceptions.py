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


class GetNotifyExceptions:
    async def get_notify_exceptions(
        self: pyrogram.Client,
        compare_sound: bool | None = None,
        compare_stories: bool | None = None,
        peer: raw.base.InputNotifyPeer | None = None,
    ) -> raw.base.Updates:
        """Returns list of chats with non-default notification settings.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            compare_sound (``bool``, *optional*):
                If set, chats with non-default sound will be returned.

            compare_stories (``bool``, *optional*):
                If set, chats with non-default notification settings for stories will be returned.

            peer (:obj:`~pyrogram.raw.base.InputNotifyPeer`, *optional*):
                If specified, only chats of the specified category will be returned.

        Returns:
            :obj:`~pyrogram.raw.base.Updates`: On success, updates are returned.
        """
        return await self.invoke(
            raw.functions.account.GetNotifyExceptions(
                compare_sound=compare_sound,
                compare_stories=compare_stories,
                peer=peer,
            )
        )
