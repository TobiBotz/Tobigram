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

# ***************************
# GENERATED FILE - DO NOT EDIT
# Source: tl:messages.editFactCheck
# ***************************

from typing import Union, Optional

import pyrogram
from pyrogram import raw
from pyrogram import types


class EditFactCheck:
    async def edit_fact_check(
        self: "pyrogram.Client",
        peer: Optional[Union[int, str]] = None,
        msg_id: Optional[int] = None,
        text_with_entities: Optional[raw.types.TextWithEntities] = None,
    ) -> "types.Message":
        """Edit the fact-check on a message (channel admins only).

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            peer (Union[int, str], *optional*): Chat where the message is
            msg_id (int, *optional*): Message ID with the fact-check
            text_with_entities (raw.types.TextWithEntities): Fact-check content as TextWithEntities (text + entities)

        Returns:
            :obj:`~pyrogram.types.Message`

        Example:
            .. code-block:: python

                await app.edit_fact_check(...)
        """

        r = await self.invoke(
            raw.functions.messages.EditFactCheck(
                peer=await self.resolve_peer(peer),
                msg_id=msg_id,
                text=text_with_entities
            )
        )

        for i in r.updates:
            if isinstance(i, (raw.types.UpdateNewMessage,
                              raw.types.UpdateNewChannelMessage,
                              raw.types.UpdateNewScheduledMessage)):
                return await types.Message._parse(
                    self, i.message,
                    {i.id: i for i in r.users},
                    {i.id: i for i in r.chats},
                    is_scheduled=isinstance(i, raw.types.UpdateNewScheduledMessage)
                )
