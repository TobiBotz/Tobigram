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

from typing import List, Optional, Union

import pyrogram
from pyrogram import enums, types

from .listen import resolve_listener_ids


class StopListening:
    async def stop_listening(
        self: "pyrogram.Client",
        listener_type: "enums.ListenerTypes" = enums.ListenerTypes.MESSAGE,
        chat_id: Optional[Union[int, str, List[Union[int, str]]]] = None,
        user_id: Optional[Union[int, str, List[Union[int, str]]]] = None,
        message_id: Optional[Union[int, List[int]]] = None,
        inline_message_id: Optional[Union[str, List[str]]] = None
    ) -> int:
        """Stop the listeners covered by the given criteria.

        Every waiter stopped this way raises ``ListenerStopped``. Criteria left
        out are wildcards, so calling this with no arguments at all stops every
        message listener on the client.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            listener_type (:obj:`~pyrogram.enums.ListenerTypes`, *optional*):
                Kind of listener to stop. Defaults to message listeners.

            chat_id (``int`` | ``str`` | List of ``int`` | ``str``, *optional*):
                Only stop listeners waiting on this chat.

            user_id (``int`` | ``str`` | List of ``int`` | ``str``, *optional*):
                Only stop listeners waiting on this user.

            message_id (``int`` | List of ``int``, *optional*):
                Only stop listeners waiting on this message.

            inline_message_id (``str`` | List of ``str``, *optional*):
                Only stop listeners waiting on this inline message.

        Returns:
            ``int``: Number of listeners that were stopped.

        Example:
            .. code-block:: python

                await app.stop_listening(chat_id=chat_id)
        """
        pattern = types.Identifier(
            chat_id=await resolve_listener_ids(self, chat_id),
            user_id=await resolve_listener_ids(self, user_id),
            message_id=message_id,
            inline_message_id=inline_message_id
        )

        return sum(
            self.listeners.stop(listener)
            for listener in self.listeners.find(listener_type, pattern)
        )
