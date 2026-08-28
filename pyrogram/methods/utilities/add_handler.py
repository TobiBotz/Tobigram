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
from pyrogram.handlers import (
    ConnectHandler, DisconnectHandler, StartHandler, StopHandler,
)
from pyrogram.handlers.handler import Handler

LIFECYCLE_HANDLERS = {
    ConnectHandler: "connect_handler",
    DisconnectHandler: "disconnect_handler",
    StartHandler: "start_handler",
    StopHandler: "stop_handler",
}


class AddHandler:
    def add_handler(
        self: "pyrogram.Client",
        handler: "Handler",
        group: int = 0
    ):
        """Register an update handler.

        .. include:: /_includes/usable-by/users-bots.rst


        You can register multiple handlers, but at most one handler within a group will be used for a single update.
        To handle the same update more than once, register your handler using a different group id (lower group id
        == higher priority). This mechanism is explained in greater details at
        :doc:`More on Updates <../../topics/more-on-updates>`.

        :obj:`~pyrogram.handlers.ConnectHandler`, :obj:`~pyrogram.handlers.DisconnectHandler`,
        :obj:`~pyrogram.handlers.StartHandler` and :obj:`~pyrogram.handlers.StopHandler` are
        lifecycle callbacks rather than update handlers: they never reach a group, *group* is
        ignored, and the client holds one of each, so registering a second one replaces the first.

        Parameters:
            handler (``Handler``):
                The handler to be registered.

            group (``int``, *optional*):
                The group identifier, defaults to 0.

        Returns:
            ``tuple``: A tuple consisting of *(handler, group)*.

        Example:
            .. code-block:: python

                from wzgram import Client
                from wzgram.handlers import MessageHandler

                async def hello(client, message):
                    print(message)

                app = Client("my_account")

                app.add_handler(MessageHandler(hello))

                app.run()
        """
        for handler_type, attribute in LIFECYCLE_HANDLERS.items():
            if isinstance(handler, handler_type):
                setattr(self, attribute, handler.callback)
                break
        else:
            self.dispatcher.add_handler(handler, group)

        return handler, group
