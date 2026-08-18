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
from pyrogram import enums, types
from pyrogram.filters import Filter

from .listen import UNSET


class WaitForMessage:
    async def wait_for_message(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        filters: Optional[Filter] = None,
        timeout: Optional[float] = UNSET
    ) -> "types.Message":
        """Wait for the next message in a chat.

        Shortcut for :meth:`~pyrogram.Client.listen` with a message listener.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Chat the message has to come from.

            filters (:obj:`~pyrogram.filters.Filter`, *optional*):
                Extra filter the message has to pass.

            timeout (``float``, *optional*):
                Seconds to wait before raising ``ListenerTimeout``. Defaults to
                the client's ``listener_timeout`` (300s).

        Returns:
            :obj:`~pyrogram.types.Message`: The matching message.

        Raises:
            ListenerTimeout: In case no message arrived in time.
            ListenerStopped: In case the listener was stopped, or the client is.

        Example:
            .. code-block:: python

                message = await app.wait_for_message(chat_id, timeout=30)
        """
        return await self.listen(
            filters=filters,
            listener_type=enums.ListenerTypes.MESSAGE,
            timeout=timeout,
            chat_id=chat_id
        )
