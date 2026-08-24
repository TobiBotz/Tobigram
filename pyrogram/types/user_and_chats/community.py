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

from datetime import datetime
from typing import Optional

from pyrogram import raw, utils

from ..object import Object


class Community(Object):
    """Represents a community.

    A community links together several supergroups, channels and bots
    around a shared topic or audience.

    Parameters:
        id (``int``):
            Unique identifier for this community.

        title (``str``):
            Title of the community.

        date (:py:obj:`~datetime.datetime`):
            Date when the community was created.

        is_creator (``bool``, *optional*):
            True, if the current user is the creator of the community.

        is_left (``bool``, *optional*):
            True, if the current user has left the community.

        is_min (``bool``, *optional*):
            True, if this community has a reduced set of fields.

        is_collapsed (``bool``, *optional*):
            True, if the community is collapsed in the dialogs list.

        dc_id (``int``, *optional*):
            Data centre ID of the community photo.
    """

    def __init__(
        self,
        *,
        id: int,
        title: str,
        date: Optional[datetime] = None,
        is_creator: Optional[bool] = None,
        is_left: Optional[bool] = None,
        is_min: Optional[bool] = None,
        is_collapsed: Optional[bool] = None,
        dc_id: Optional[int] = None,
    ):
        super().__init__()

        self.id = id
        self.title = title
        self.date = date
        self.is_creator = is_creator
        self.is_left = is_left
        self.is_min = is_min
        self.is_collapsed = is_collapsed
        self.dc_id = dc_id

    @staticmethod
    def _parse(client, community: "raw.types.Community") -> Optional["Community"]:
        # the chats map of an update is keyed by id across every peer kind, so a
        # lookup by community id can hand back a Channel
        if not isinstance(community, raw.types.Community):
            return None

        return Community(
            id=community.id,
            title=community.title,
            date=utils.timestamp_to_datetime(community.date),
            is_creator=community.creator,
            is_left=community.left,
            is_min=community.min,
            is_collapsed=community.collapsed_in_dialogs,
            dc_id=getattr(getattr(community, "photo", None), "dc_id", None),
        )
