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

from typing import Optional

from pyrogram import raw

from ..object import Object


class CommunityChatRemoved(Object):
    """A chat has been removed from a community.

    Parameters:
        community_id (``int``):
            The identifier of the community the chat was removed from.
    """

    def __init__(
        self,
        *,
        community_id: Optional[int] = None,
    ):
        super().__init__()

        self.community_id = community_id

    @staticmethod
    def _parse(
        action: "raw.types.MessageActionChangeCommunity",
    ) -> Optional["CommunityChatRemoved"]:
        if action.community_id is not None:
            return None

        return CommunityChatRemoved(
            community_id=action.community_id,
        )
