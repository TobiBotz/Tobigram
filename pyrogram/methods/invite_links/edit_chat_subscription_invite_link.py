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
from pyrogram import raw, types


class EditChatSubscriptionInviteLink:
    async def edit_chat_subscription_invite_link(
        self: pyrogram.Client,
        chat_id: int | str,
        invite_link: str,
        name: str | None = None,
    ) -> types.ChatInviteLink:
        """Edit a subscription invite link created by the bot.

        The bot must have the ``can_invite_users`` administrator right.
        Returns the edited invite link as a :obj:`~pyrogram.types.ChatInviteLink` object.

        .. include:: /_includes/usable-by/bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target channel.

            invite_link (``str``):
                The subscription invite link to edit.

            name (``str``, *optional*):
                Invite link name; 0-32 characters.

        Returns:
            :obj:`~pyrogram.types.ChatInviteLink`: On success, the edited invite link is returned.

        Example:
            .. code-block:: python

                # Rename an existing subscription invite link
                link = await app.edit_chat_subscription_invite_link(
                    chat_id=chat_id,
                    invite_link="https://t.me/+xxxx",
                    name="VIP Members",
                )
        """
        r = await self.invoke(
            raw.functions.messages.EditExportedChatInvite(
                peer=await self.resolve_peer(chat_id),
                link=invite_link,
                title=name,
            )
        )

        users = {i.id: i for i in r.users}
        return types.ChatInviteLink._parse(self, r.invite, users)
