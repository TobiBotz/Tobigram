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
