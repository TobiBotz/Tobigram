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

import pyrogram
from pyrogram.filters import Filter

if TYPE_CHECKING:
    from collections.abc import Callable


class OnStreamEnd:
    def on_stream_end(self=None, filters=None, group: int = 0) -> Callable:
        """Decorator for handling when an audio or video stream in a voice chat ends.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            filters (:obj:`~pyrogram.filters`, *optional*):
                Pass one or more filters.

            group (``int``, *optional*):
                The group identifier, defaults to 0.

        Example:
            .. code-block:: python

                @app.on_stream_end()
                async def play_next(client, update):
                    print(f"Song ended in chat {update.chat_id}!")
        """

        def decorator(func: Callable) -> Callable:
            if isinstance(self, pyrogram.Client):
                self.add_handler(pyrogram.handlers.StreamEndedHandler(func, filters), group)
            elif isinstance(self, Filter) or self is None:
                if not hasattr(func, "handlers"):
                    func.handlers = []

                handler_filters, handler_group = pyrogram.utils.unbound_handler_args(
                    self, filters, group
                )

                func.handlers.append(
                    (
                        pyrogram.handlers.StreamEndedHandler(func, handler_filters),
                        handler_group,
                    )
                )

            return func

        return decorator
