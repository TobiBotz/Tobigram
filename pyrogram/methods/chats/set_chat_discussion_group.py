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


class SetChatDiscussionGroup:
    async def set_chat_discussion_group(
        self: "pyrogram.Client",
        chat_id: int | str | None = None,
        discussion_chat_id: int | str | None = None,
    ) -> bool:
        """Link or unlink a discussion group to a channel.

        Requires the ``can_change_info`` administrator right in the channel, and the
        ``can_pin_messages`` member right in the group.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``, *optional*):
                Unique identifier (int) or username (str) of the target channel.
                Pass None to unlink the group given in ``discussion_chat_id`` from its channel.

            discussion_chat_id (``int`` | ``str``, *optional*):
                Unique identifier (int) or username (str) of the discussion group.
                Pass None to remove the current discussion group of the channel.

        Returns:
            ``bool``: On success, True is returned.

        Raises:
            ValueError: In case both arguments are None, or one of them does not belong to a channel.

        Example:
            .. code-block:: python

                await app.set_chat_discussion_group("@channel", "@group")

                await app.set_chat_discussion_group(chat_id="@channel")
        """

        if chat_id is None and discussion_chat_id is None:
            raise ValueError("At least one of chat_id or discussion_chat_id must be given")

        broadcast = raw.types.InputChannelEmpty()
        group = raw.types.InputChannelEmpty()

        if chat_id is not None:
            broadcast = await self.resolve_peer(chat_id)

            if not isinstance(
                broadcast, (raw.types.InputPeerChannel, raw.types.InputPeerChannelFromMessage)
            ):
                raise ValueError(f'The chat_id "{chat_id}" does not belong to a channel')

        if discussion_chat_id is not None:
            group = await self.resolve_peer(discussion_chat_id)

            if not isinstance(
                group, (raw.types.InputPeerChannel, raw.types.InputPeerChannelFromMessage)
            ):
                raise ValueError(
                    f'The discussion_chat_id "{discussion_chat_id}" does not belong to a supergroup'
                )

        return bool(
            await self.invoke(
                raw.functions.channels.SetDiscussionGroup(
                    broadcast=(
                        utils.get_input_channel(broadcast)
                        if isinstance(broadcast, raw.types.InputPeerChannelFromMessage)
                        else broadcast
                    ),
                    group=(
                        utils.get_input_channel(group)
                        if isinstance(group, raw.types.InputPeerChannelFromMessage)
                        else group
                    ),
                )
            )
        )
