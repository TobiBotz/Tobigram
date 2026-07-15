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

from pyrogram import raw
from ..object import Object


class PollStats(Object):
    """Statistics for a poll sent in a message.

    Parameters:
        votes_graph (:obj:`~pyrogram.raw.base.StatsGraph`):
            A graph showing the number of votes received by each answer option over time.
    """

    def __init__(
        self,
        *,
        votes_graph: "raw.base.StatsGraph",
    ):
        super().__init__()

        self.votes_graph = votes_graph

    @staticmethod
    def _parse(poll_stats: "raw.types.stats.PollStats") -> "PollStats":
        return PollStats(
            votes_graph=poll_stats.votes_graph
        )
