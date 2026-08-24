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

from typing import Dict, Optional

from pyrogram import raw, types

from ..object import Object


class CommunityChatJoined(Object):
    """A chat was joined by a user from a community.

    Parameters:
        community_id (``int``):
            The identifier of the community the chat was joined from.

        community (:obj:`~pyrogram.types.Community`, *optional*):
            The community the chat was joined from, if available.
    """

    def __init__(
        self,
        *,
        community_id: Optional[int] = None,
        community: Optional["types.Community"] = None,
    ):
        super().__init__()

        self.community_id = community_id
        self.community = community

    @staticmethod
    def _parse(
        client,
        action: "raw.types.MessageActionChatJoinedViaCommunity",
        chats: Dict[int, "raw.base.Chat"],
    ) -> "CommunityChatJoined":
        return CommunityChatJoined(
            community_id=action.community_id,
            community=types.Community._parse(client, chats.get(action.community_id)),
        )
