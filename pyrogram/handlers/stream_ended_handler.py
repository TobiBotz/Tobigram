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

from typing import TYPE_CHECKING
from .handler import Handler

if TYPE_CHECKING:
    from collections.abc import Callable


class StreamEndedHandler(Handler):
    """The StreamEnded handler class. Used to handle when an audio/video stream in a voice chat ends.

    It is intended to be used with :meth:`~pyrogram.Client.add_handler` or
    the :meth:`~pyrogram.Client.on_stream_end` decorator.

    Parameters:
        callback (``Callable``):
            Pass a function that will be called when a stream ends. It takes *(client, update)*
            as positional arguments.

        filters (:obj:`Filters`, *optional*):
            Pass one or more filters.
    """

    def __init__(self, callback: Callable, filters=None):
        super().__init__(callback, filters)
