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
from pyrogram import enums, raw


class SetMainProfileTab:
    async def set_main_profile_tab(
        self: "pyrogram.Client", chat_id: int | str, main_profile_tab: "enums.ProfileTab"
    ) -> bool:
        """Change the main profile tab of your account or of a channel.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                Pass "me" or "self" to change the tab of your own profile.

            main_profile_tab (:obj:`~pyrogram.enums.ProfileTab`):
                The tab to open first.

        Returns:
            ``bool``: On success, True is returned.

        Example:
            .. code-block:: python

                await app.set_main_profile_tab("me", enums.ProfileTab.GIFTS)
        """

        peer = await self.resolve_peer(chat_id)

        if isinstance(peer, raw.types.InputPeerSelf):
            r = await self.invoke(
                raw.functions.account.SetMainProfileTab(tab=main_profile_tab.value())
            )
        else:
            r = await self.invoke(
                raw.functions.channels.SetMainProfileTab(channel=peer, tab=main_profile_tab.value())
            )

        return bool(r)
