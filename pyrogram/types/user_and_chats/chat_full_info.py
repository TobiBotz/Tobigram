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

from typing import Dict, List, Optional, Union

from pyrogram import raw

from ..object import Object


class ChatFullInfo(Object):
    """Contains full information about a chat.

    Parameters:
        community (:obj:`~pyrogram.types.Community`, *optional*):
            Information about the community this chat belongs to.
    """

    def __init__(
        self,
        *,
        community: Optional["types.Community"] = None,
    ):
        super().__init__()

        self.community = community

    @staticmethod
    def _parse(
        client,
        chat_full: "raw.base.ChatFull",
        chats: Optional[Union[Dict[int, "raw.base.Chat"], List["raw.base.Chat"]]] = None,
    ) -> Optional["ChatFullInfo"]:
        if chat_full is None:
            return None

        from pyrogram.types import Community

        community = None
        if isinstance(chat_full, raw.types.CommunityFull):
            community_id = chat_full.id
            community_raw = None

            if chats is not None:
                if isinstance(chats, dict):
                    community_raw = chats.get(community_id)
                else:
                    for c in chats:
                        if isinstance(c, raw.types.Community) and c.id == community_id:
                            community_raw = c
                            break

            if community_raw is not None:
                community = Community._parse(client, community_raw)
            else:
                community = Community(
                    id=community_id,
                    title="",
                    date=None,
                )

        return ChatFullInfo(
            community=community,
        )
