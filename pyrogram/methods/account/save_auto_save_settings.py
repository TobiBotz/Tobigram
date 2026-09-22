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


class SaveAutoSaveSettings:
    async def save_auto_save_settings(
        self: pyrogram.Client,
        settings: raw.base.AutoSaveSettings,
        users: bool | None = None,
        chats: bool | None = None,
        broadcasts: bool | None = None,
        peer: int | str | raw.base.InputPeer | None = None,
    ) -> bool:
        """Modify autosave settings.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            settings (:obj:`~pyrogram.raw.base.AutoSaveSettings`):
                The new autosave settings.

            users (``bool``, *optional*):
                Whether the new settings should affect all private chats.

            chats (``bool``, *optional*):
                Whether the new settings should affect all groups.

            broadcasts (``bool``, *optional*):
                Whether the new settings should affect all channels.

            peer (``int`` | ``str`` | :obj:`~pyrogram.raw.base.InputPeer`, *optional*):
                Whether the new settings should affect a specific peer.

        Returns:
            ``bool``: On success, True is returned.
        """
        input_peer = None
        if peer is not None:
            input_peer = (
                peer if isinstance(peer, raw.base.InputPeer) else await self.resolve_peer(peer)
            )

        return await self.invoke(
            raw.functions.account.SaveAutoSaveSettings(
                settings=settings,
                users=users,
                chats=chats,
                broadcasts=broadcasts,
                peer=input_peer,
            )
        )
