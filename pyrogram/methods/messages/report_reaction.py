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

import pyrogram
from pyrogram import raw


class ReportReaction:
    async def report_reaction(
        self: pyrogram.Client,
        chat_id: int | str,
        message_id: int,
        reaction_peer: int | str,
    ) -> bool:
        """Report an abusive or inappropriate reaction on a message.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            message_id (``int``):
                Unique identifier of the message containing the reaction.

            reaction_peer (``int`` | ``str``):
                Unique identifier (int) or username (str) of the peer who reacted.

        Returns:
            ``bool``: True on success.

        Example:
            .. code-block:: python

                # Report a reaction
                await app.report_reaction(chat_id, message_id, reaction_peer)
        """
        peer = await self.resolve_peer(chat_id)
        r_peer = await self.resolve_peer(reaction_peer)

        return bool(
            await self.invoke(
                raw.functions.messages.ReportReaction(
                    peer=peer,
                    id=message_id,
                    reaction_peer=r_peer,
                )
            )
        )
