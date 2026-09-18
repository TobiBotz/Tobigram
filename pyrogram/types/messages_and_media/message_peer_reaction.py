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

from datetime import datetime

import pyrogram
from pyrogram import raw, types, utils

from ..object import Object


class MessagePeerReaction(Object):
    """Contains information about a reaction added to a message by a peer.

    Parameters:
        user (:obj:`~pyrogram.types.User`, *optional*):
            The user who reacted to the message, if the reaction was added by a user.

        chat (:obj:`~pyrogram.types.Chat`, *optional*):
            The chat / channel that reacted to the message, if sent as a channel.

        reaction (:obj:`~pyrogram.types.Reaction`):
            The reaction added to the message.

        date (:py:obj:`~datetime.datetime`):
            Date the reaction was added.

        big (``bool``, *optional*):
            True, if a bigger / animated reaction effect was used.

        unread (``bool``, *optional*):
            True, if the reaction is unread by the current user.

        my (``bool``, *optional*):
            True, if this reaction was sent by the current user.
    """

    def __init__(
        self,
        *,
        client: pyrogram.Client | None = None,
        user: types.User | None = None,
        chat: types.Chat | None = None,
        reaction: types.Reaction,
        date: datetime,
        big: bool = False,
        unread: bool = False,
        my: bool = False,
    ):
        super().__init__(client)

        self.user = user
        self.chat = chat
        self.reaction = reaction
        self.date = date
        self.big = big
        self.unread = unread
        self.my = my

    @staticmethod
    def _parse(
        client: pyrogram.Client,
        peer_reaction: raw.types.MessagePeerReaction,
        users: dict[int, raw.types.User],
        chats: dict[int, raw.types.Chat],
    ) -> MessagePeerReaction:
        peer_id = utils.get_raw_peer_id(peer_reaction.peer_id)
        user = types.User._parse(client, users[peer_id]) if peer_id in users else None
        chat = (
            types.Chat._parse_chat(client, chats[peer_id])
            if (peer_id in chats and user is None)
            else None
        )

        return MessagePeerReaction(
            client=client,
            user=user,
            chat=chat,
            reaction=types.Reaction._parse(client, peer_reaction.reaction),
            date=utils.timestamp_to_datetime(peer_reaction.date),
            big=getattr(peer_reaction, "big", False) or False,
            unread=getattr(peer_reaction, "unread", False) or False,
            my=getattr(peer_reaction, "my", False) or False,
        )
