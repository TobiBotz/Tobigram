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

from typing import Optional, Union

import pyrogram
from pyrogram import enums, raw


class SendPaidReaction:
    async def send_paid_reaction(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        message_id: int,
        amount: int,
        privacy: Optional["enums.PaidReactionPrivacy"] = None,
        send_as: Optional[Union[int, str]] = None
    ) -> bool:
        """Send a paid reaction to a message, spending Telegram Stars.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            message_id (``int``):
                Identifier of the message to react to.

            amount (``int``):
                Number of Telegram Stars to spend, one star per reaction.

            privacy (:obj:`~pyrogram.enums.PaidReactionPrivacy`, *optional*):
                Who the reaction is shown as. Defaults to the account setting.

            send_as (``int`` | ``str``, *optional*):
                Chat to react as. Required when *privacy* is
                :obj:`~pyrogram.enums.PaidReactionPrivacy.CHAT`.

        Returns:
            ``bool``: On success, True is returned.

        Raises:
            ValueError: In case *privacy* is CHAT and no *send_as* chat is given.

        Example:
            .. code-block:: python

                # Send five stars
                await app.send_paid_reaction(chat_id, message_id, 5)

                # Send them anonymously
                await app.send_paid_reaction(
                    chat_id, message_id, 5,
                    privacy=enums.PaidReactionPrivacy.ANONYMOUS
                )
        """
        private = None

        if privacy is not None:
            if privacy == enums.PaidReactionPrivacy.CHAT:
                if send_as is None:
                    raise ValueError("send_as is required when privacy is CHAT")

                private = privacy.value(peer=await self.resolve_peer(send_as))
            else:
                private = privacy.value()

        await self.invoke(
            raw.functions.messages.SendPaidReaction(
                peer=await self.resolve_peer(chat_id),
                msg_id=message_id,
                count=amount,
                random_id=self.rnd_id(),
                private=private
            )
        )

        return True
