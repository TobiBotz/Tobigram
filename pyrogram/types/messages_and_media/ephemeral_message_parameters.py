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

from ..object import Object


class EphemeralMessageParameters(Object):
    """Describes an ephemeral message to send in place of an ordinary one.

    Pass it to any send method to send that message as an :doc:`ephemeral message
    </features/ephemeral-messages>` — visible only to one person and absent from the
    chat's history — rather than as a normal one.

    Parameters:
        receiver_user_id (``int`` | ``str``):
            Unique identifier (int) or username (str) of the user who will receive the
            message. There is no guarantee they will, especially if they are offline.

        callback_query_id (``str``, *optional*):
            Identifier of the callback query which triggered the message, if any.

        replace_callback_query_message (``bool``, *optional*):
            Pass True if the ephemeral message must be shown in place of the message the
            callback query came from. Must be False for callback queries that came from an
            ephemeral message, which are edited with the
            :meth:`~pyrogram.Client.edit_ephemeral_message_text` family instead.
    """

    def __init__(
        self,
        receiver_user_id: Union[int, str],
        callback_query_id: Optional[str] = None,
        replace_callback_query_message: Optional[bool] = None,
    ):
        super().__init__()

        self.receiver_user_id = receiver_user_id
        self.callback_query_id = callback_query_id
        self.replace_callback_query_message = replace_callback_query_message
