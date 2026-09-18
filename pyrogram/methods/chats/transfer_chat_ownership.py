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


class TransferChatOwnership:
    async def transfer_chat_ownership(
        self: "pyrogram.Client", chat_id: int | str, user_id: int | str, password: str
    ) -> bool:
        """Transfer the ownership of a supergroup or a channel to another user.

        Requires owner privileges and two-step verification enabled on your account.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            user_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the new owner.

            password (``str``):
                The two-step verification password of the current user.

        Returns:
            ``bool``: On success, True is returned.

        Raises:
            ValueError: In case the chat is not a supergroup or a channel, or the new owner is not a user.

        Example:
            .. code-block:: python

                await app.transfer_chat_ownership(chat_id, user_id, "password")
        """

        peer_chat = await self.resolve_peer(chat_id)
        peer_user = await self.resolve_peer(user_id)

        if not isinstance(peer_chat, raw.types.InputPeerChannel):
            raise ValueError("The chat_id must belong to a supergroup or a channel")

        if not isinstance(
            peer_user,
            (raw.types.InputPeerUser, raw.types.InputPeerUserFromMessage, raw.types.InputPeerSelf),
        ):
            raise ValueError("The user_id must belong to a user")

        r = await self.invoke(
            raw.functions.messages.EditChatCreator(
                peer=peer_chat,
                user_id=peer_user,
                password=utils.compute_password_check(
                    await self.invoke(raw.functions.account.GetPassword()), password
                ),
            )
        )

        return bool(r)
