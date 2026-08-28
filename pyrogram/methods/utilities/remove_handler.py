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

import pyrogram
from pyrogram.handlers.handler import Handler

from .add_handler import LIFECYCLE_HANDLERS


class RemoveHandler:
    def remove_handler(
        self: "pyrogram.Client",
        handler: "Handler",
        group: int = 0
    ):
        """Remove a previously-registered update handler.

        .. include:: /_includes/usable-by/users-bots.rst


        Make sure to provide the right group where the handler was added in. You can use the return value of the
        :meth:`~pyrogram.Client.add_handler` method, a tuple of *(handler, group)*, and pass it directly.

        Parameters:
            handler (``Handler``):
                The handler to be removed.

            group (``int``, *optional*):
                The group identifier, defaults to 0.

        Returns:
            ``None``: The handler stops receiving updates once it returns.

        Example:
            .. code-block:: python

                from wzgram import Client
                from wzgram.handlers import MessageHandler

                async def hello(client, message):
                    print(message)

                app = Client("my_account")

                handler = app.add_handler(MessageHandler(hello))

                # Starred expression to unpack (handler, group)
                app.remove_handler(*handler)

                app.run()
        """
        for handler_type, attribute in LIFECYCLE_HANDLERS.items():
            if isinstance(handler, handler_type):
                if getattr(self, attribute) is handler.callback:
                    setattr(self, attribute, None)

                break
        else:
            self.dispatcher.remove_handler(handler, group)
