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

from typing import Callable, List, Optional, Union

import pyrogram
from pyrogram import enums, types
from pyrogram.filters import Filter

from .listen import UNSET, resolve_listener_ids


class RegisterNextStepHandler:
    async def register_next_step_handler(
        self: "pyrogram.Client",
        callback: Callable,
        filters: Optional[Filter] = None,
        listener_type: "enums.ListenerTypes" = enums.ListenerTypes.MESSAGE,
        timeout: Optional[float] = UNSET,
        unallowed_click_alert: Union[bool, str] = True,
        chat_id: Optional[Union[int, str, List[Union[int, str]]]] = None,
        user_id: Optional[Union[int, str, List[Union[int, str]]]] = None,
        message_id: Optional[Union[int, List[int]]] = None,
        inline_message_id: Optional[Union[str, List[str]]] = None
    ) -> "types.Listener":
        """Run a callback once, on the next update matching the given criteria.

        The callback form of :meth:`~pyrogram.Client.listen`, for flows that
        would rather not park a coroutine. It does not hold a dispatcher worker,
        so it scales further than ``listen`` for long or abandoned conversations.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            callback (``Callable``):
                Called with *(client, update)* when a matching update arrives.
                May be a coroutine function or a plain one.

            filters (:obj:`~pyrogram.filters.Filter`, *optional*):
                Extra filter the update has to pass.

            listener_type (:obj:`~pyrogram.enums.ListenerTypes`, *optional*):
                Kind of update to wait for. Defaults to a new message.

            timeout (``float``, *optional*):
                Seconds before the listener is dropped. Defaults to the client's
                ``listener_timeout`` (300s). Pass None to keep it forever.

            unallowed_click_alert (``bool`` | ``str``, *optional*):
                For callback query listeners, answer clicks coming from a user
                this listener does not expect. Pass a string to set the text.

            chat_id (``int`` | ``str`` | List of ``int`` | ``str``, *optional*):
                Chat the update has to come from.

            user_id (``int`` | ``str`` | List of ``int`` | ``str``, *optional*):
                User the update has to come from.

            message_id (``int`` | List of ``int``, *optional*):
                Message the update has to belong to.

            inline_message_id (``str`` | List of ``str``, *optional*):
                Inline message the update has to belong to.

        Returns:
            :obj:`~pyrogram.types.Listener`: The registered listener, which can
            be handed to :meth:`~pyrogram.Client.stop_listening` criteria or
            dropped with ``client.listeners.stop(listener)``.

        Raises:
            ListenerStopped: In case the client is stopping.
            ListenerLimitReached: In case no listener slot was available.

        Example:
            .. code-block:: python

                async def got_name(client, message):
                    await message.reply(f"Hello {message.text}")

                await app.send_message(chat_id, "What is your name?")
                await app.register_next_step_handler(got_name, chat_id=chat_id)
        """
        if timeout is UNSET:
            timeout = self.listener_timeout

        identifier = types.Identifier(
            chat_id=await resolve_listener_ids(self, chat_id),
            user_id=await resolve_listener_ids(self, user_id),
            message_id=message_id,
            inline_message_id=inline_message_id
        )

        listener = types.Listener(
            listener_type=listener_type,
            identifier=identifier,
            filters=filters,
            callback=callback,
            unallowed_click_alert=unallowed_click_alert
        )

        self.listeners.add(listener, timeout)

        return listener
