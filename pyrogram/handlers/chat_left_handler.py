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

from typing import TYPE_CHECKING, Any

import pyrogram

from .handler import Handler

if TYPE_CHECKING:
    from pyrogram.types import Update
    from collections.abc import Callable
    from pyrogram.filters import Filter


class ChatLeftHandler(Handler):
    """The ChatLeft handler class. Used to handle chat member leave events.

    It triggers whenever a member leaves voluntarily, or is kicked / banned from a chat.
    It is intended to be used with :meth:`~pyrogram.Client.add_handler`.

    For a nicer way to register this handler, have a look at the
    :meth:`~pyrogram.Client.on_chat_left` decorator.

    Parameters:
        callback (``Callable``):
            Pass a function that will be called when a chat member leaves. It takes
            *(client, chat_member_updated)* as positional arguments.

        filters (:obj:`~pyrogram.filters`, *optional*):
            Pass one or more filters to allow only a subset of updates to be passed
            in your callback function.
    """

    def __init__(
        self,
        callback: Callable[[pyrogram.Client, pyrogram.types.ChatMemberUpdated], Any],
        filters: Filter | None = None,
    ):
        super().__init__(callback, filters)

    async def check(self, client: pyrogram.Client, update: Update) -> bool:
        if not isinstance(update, pyrogram.types.ChatMemberUpdated):
            return False

        if not update.is_left:
            return False

        return await super().check(client, update)
