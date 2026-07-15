from typing import Union

import pyrogram
from pyrogram import raw, types, utils


class DeleteParticipantReaction:
    async def delete_participant_reaction(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        message_id: int,
        participant_id: Union[int, str],
    ) -> "types.Message":
        """Remove all reactions of a specific participant from a single message.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            message_id (``int``):
                Identifier of the message.

            participant_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the participant whose reactions will be removed.

        Returns:
            :obj:`~pyrogram.types.Message`: On success, the updated message is returned.

        Example:
            .. code-block:: python

                # Remove all reactions by a user from a specific message
                await app.delete_participant_reaction(chat_id, message_id, participant_id)
        """
        r = await self.invoke(
            raw.functions.messages.DeleteParticipantReaction(
                peer=await self.resolve_peer(chat_id),
                msg_id=message_id,
                participant=await self.resolve_peer(participant_id)
            )
        )

        return next(iter(await utils.parse_messages(client=self, messages=r)), None)
