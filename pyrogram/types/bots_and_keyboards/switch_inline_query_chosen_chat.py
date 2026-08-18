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

from typing import List, Optional

from pyrogram import raw

from ..object import Object


class SwitchInlineQueryChosenChat(Object):
    """An inline button that switches the current user to inline mode in a chosen chat.

    Parameters:
        query (``str``, *optional*):
            The default inline query to be inserted in the input field.
            If left empty, only the bot username will be inserted.

        allow_user_chats (``bool``, *optional*):
            True, if private chats with users can be chosen.

        allow_bot_chats (``bool``, *optional*):
            True, if private chats with bots can be chosen.

        allow_group_chats (``bool``, *optional*):
            True, if group and supergroup chats can be chosen.

        allow_channel_chats (``bool``, *optional*):
            True, if channel chats can be chosen.
    """

    def __init__(
        self,
        query: Optional[str] = None,
        allow_user_chats: Optional[bool] = None,
        allow_bot_chats: Optional[bool] = None,
        allow_group_chats: Optional[bool] = None,
        allow_channel_chats: Optional[bool] = None
    ):
        super().__init__()

        self.query = query
        self.allow_user_chats = allow_user_chats
        self.allow_bot_chats = allow_bot_chats
        self.allow_group_chats = allow_group_chats
        self.allow_channel_chats = allow_channel_chats

    @staticmethod
    def _parse(
        query: Optional[str],
        peer_types: Optional[List["raw.base.InlineQueryPeerType"]]
    ) -> "SwitchInlineQueryChosenChat":
        kinds = {type(peer_type) for peer_type in peer_types or []}

        return SwitchInlineQueryChosenChat(
            query=query,
            allow_user_chats=raw.types.InlineQueryPeerTypePM in kinds or None,
            allow_bot_chats=raw.types.InlineQueryPeerTypeBotPM in kinds or None,
            allow_group_chats=bool(
                kinds & {
                    raw.types.InlineQueryPeerTypeChat,
                    raw.types.InlineQueryPeerTypeMegagroup
                }
            ) or None,
            allow_channel_chats=raw.types.InlineQueryPeerTypeBroadcast in kinds or None
        )

    def _peer_types(self) -> List["raw.base.InlineQueryPeerType"]:
        peer_types = []

        if self.allow_user_chats:
            peer_types.append(raw.types.InlineQueryPeerTypePM())

        if self.allow_bot_chats:
            peer_types.append(raw.types.InlineQueryPeerTypeBotPM())

        if self.allow_group_chats:
            peer_types.append(raw.types.InlineQueryPeerTypeChat())
            peer_types.append(raw.types.InlineQueryPeerTypeMegagroup())

        if self.allow_channel_chats:
            peer_types.append(raw.types.InlineQueryPeerTypeBroadcast())

        return peer_types
