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

from .send_ephemeral_message import SendEphemeralMessage
from .delete_ephemeral_message import DeleteEphemeralMessage
from .get_welcome_messages import GetWelcomeMessages
from .delete_welcome_message import DeleteWelcomeMessage
from .delete_all_welcome_messages import DeleteAllWelcomeMessages
from .edit_ephemeral_message_text import EditEphemeralMessageText
from .edit_ephemeral_message_caption import EditEphemeralMessageCaption
from .edit_ephemeral_message_media import EditEphemeralMessageMedia
from .edit_ephemeral_message_reply_markup import EditEphemeralMessageReplyMarkup


class Ephemeral(
    SendEphemeralMessage,
    DeleteEphemeralMessage,
    GetWelcomeMessages,
    DeleteWelcomeMessage,
    DeleteAllWelcomeMessages,
    EditEphemeralMessageText,
    EditEphemeralMessageCaption,
    EditEphemeralMessageMedia,
    EditEphemeralMessageReplyMarkup,
):
    pass
