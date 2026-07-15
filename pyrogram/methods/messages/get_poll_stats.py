from typing import Union

import pyrogram
from pyrogram import raw, types


class GetPollStats:
    async def get_poll_stats(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        message_id: int,
        dark: bool = False,
    ) -> "types.PollStats":
        """Get statistics for a poll sent in a message.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            message_id (``int``):
                Identifier of the message containing the poll.

            dark (``bool``, *optional*):
                Whether to use a dark theme for the statistics graph.
                Defaults to False.

        Returns:
            :obj:`~pyrogram.types.PollStats`: On success, the poll statistics are returned.

        Example:
            .. code-block:: python

                # Get poll statistics
                stats = await app.get_poll_stats(chat_id, message_id)
                print(stats.votes_graph)
        """
        r = await self.invoke(
            raw.functions.stats.GetPollStats(
                peer=await self.resolve_peer(chat_id),
                msg_id=message_id,
                dark=dark
            )
        )

        return types.PollStats._parse(r)
