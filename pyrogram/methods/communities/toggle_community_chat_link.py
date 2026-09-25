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
from pyrogram import raw, utils


class ToggleCommunityChatLink:
    async def toggle_community_chat_link(
        self: pyrogram.Client,
        community_id: int | str,
        chat_id: int | str,
        visible: bool | None = None,
        hidden: bool | None = None,
        deleted: bool | None = None,
    ) -> bool:
        """Link, unlink, hide, or make visible a chat/channel in a community.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            community_id (``int`` | ``str``):
                Target community identifier.

            chat_id (``int`` | ``str``):
                Target chat/channel to link or modify.

            visible (``bool``, *optional*):
                Whether the link should be visible.

            hidden (``bool``, *optional*):
                Whether the link should be hidden.

            deleted (``bool``, *optional*):
                Whether the link should be deleted (unlinked).

        Returns:
            ``bool``: True on success.

        Example:
            .. code-block:: python

                # Link chat visibly
                await app.toggle_community_chat_link(community_id, chat_id, visible=True)

                # Unlink chat
                await app.toggle_community_chat_link(community_id, chat_id, deleted=True)
        """
        comm_peer = await self.resolve_peer(community_id)
        chat_peer = await self.resolve_peer(chat_id)

        return await self.invoke(
            raw.functions.communities.TogglePeerLink(
                community=utils.get_input_channel(comm_peer),
                peer=chat_peer,
                visible=visible,
                hidden=hidden,
                deleted=deleted,
            )
        )
