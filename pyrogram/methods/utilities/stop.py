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

import logging

import pyrogram
from pyrogram import utils

log = logging.getLogger(__name__)


class Stop:
    async def stop(
        self: "pyrogram.Client",
        block: bool = True
    ):
        """Stop the Client.

        .. include:: /_includes/usable-by/users-bots.rst


        This method disconnects the client from Telegram and stops the underlying tasks.

        Parameters:
            block (``bool``, *optional*):
                Blocks the code execution until the client has been stopped. It is useful with ``block=False`` in case
                you want to stop the own client *within* a handler in order not to cause a deadlock.
                Defaults to True.

        Returns:
            :obj:`~pyrogram.Client`: The stopped client itself.

        Stopping a client that is already stopped does nothing. A client that
        connected but never finished starting up is still disconnected.

        Example:
            .. code-block:: python

                from pyrogram import Client

                app = Client("my_account")


                async def main():
                    await app.start()
                    ...  # Invoke API methods
                    await app.stop()


                app.run(main())
        """

        async def do_it():
            if self.is_initialized:
                try:
                    await self.terminate()
                except Exception:
                    log.exception("Error while terminating client")

            if self.is_connected:
                try:
                    await self.disconnect()
                except Exception:
                    log.exception("Error while disconnecting client")

        if block:
            await do_it()
        else:
            utils.run_in_background(do_it(), self.loop)

        return self
