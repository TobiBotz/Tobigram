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
from pyrogram import raw


class SetChatMemberTag:
    async def set_chat_member_tag(
        self: "pyrogram.Client",
        chat_id: int | str,
        user_id: int | str,
        tag: str | None = None,
    ) -> bool:
        """Set a custom tag for a member of a group or a supergroup.

        Requires the ``can_manage_tags`` administrator right.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            user_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target user.

            tag (``str``, *optional*):
                New tag for the member, 0-16 characters, emoji are not allowed.
                Pass None to remove the current tag.

        Returns:
            ``bool``: On success, True is returned.

        Example:
            .. code-block:: python

                await app.set_chat_member_tag(chat_id, user_id, "Cool guy")
        """

        await self.invoke(
            raw.functions.messages.EditChatParticipantRank(
                peer=await self.resolve_peer(chat_id),
                participant=await self.resolve_peer(user_id),
                rank=tag or "",
            )
        )

        return True
