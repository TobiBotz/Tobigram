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

from typing import TYPE_CHECKING

from ..object import Object

if TYPE_CHECKING:
    import pyrogram


class GroupCallSettings(Object):
    """Contains settings of a group voice chat or live stream.

    Parameters:
        join_muted (``bool``, *optional*):
            Whether new participants join muted by default.

        messages_enabled (``bool``, *optional*):
            Whether chat messages are enabled during the call.

        listeners_hidden (``bool``, *optional*):
            Whether listeners who are not speaking are hidden in the call UI.

        send_paid_messages_stars (``int``, *optional*):
            Minimum number of Telegram stars required to send paid messages.

        can_change_join_muted (``bool``, *optional*):
            Whether current user/admin has permission to toggle the join_muted setting.

        can_change_messages_enabled (``bool``, *optional*):
            Whether current user/admin has permission to toggle chat messages.
    """

    def __init__(
        self,
        *,
        client: pyrogram.Client = None,
        join_muted: bool = False,
        messages_enabled: bool = True,
        listeners_hidden: bool | None = None,
        send_paid_messages_stars: int | None = None,
        can_change_join_muted: bool | None = None,
        can_change_messages_enabled: bool | None = None,
    ):
        super().__init__(client)
        self.join_muted = join_muted
        self.messages_enabled = messages_enabled
        self.listeners_hidden = listeners_hidden
        self.send_paid_messages_stars = send_paid_messages_stars
        self.can_change_join_muted = can_change_join_muted
        self.can_change_messages_enabled = can_change_messages_enabled
