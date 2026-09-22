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

from .get_broadcast_stats import GetBroadcastStats
from .get_megagroup_stats import GetMegagroupStats
from .get_message_public_forwards import GetMessagePublicForwards
from .get_message_stats import GetMessageStats
from .get_story_public_forwards import GetStoryPublicForwards
from .get_story_stats import GetStoryStats
from .load_async_graph import LoadAsyncGraph


class Stats(
    GetBroadcastStats,
    GetMegagroupStats,
    GetMessagePublicForwards,
    GetMessageStats,
    GetStoryPublicForwards,
    GetStoryStats,
    LoadAsyncGraph,
):
    pass
