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

import asyncio
import logging
from typing import List

log = logging.getLogger(__name__)

import pyrogram
from .idle import idle


async def compose(
    clients: List["pyrogram.Client"],
    sequential: bool = False
):
    """Run multiple clients at once.

        .. include:: /_includes/usable-by/users-bots.rst


    This method can be used to run multiple clients at once and can be found directly in the ``pyrogram`` package.

    If you want to run a single client, you can use Client's bound method :meth:`~pyrogram.Client.run`.

    Parameters:
        clients (List of :obj:`~pyrogram.Client`):
            A list of client objects to run.

        sequential (``bool``, *optional*):
            Pass True to run clients sequentially.
            Defaults to False (run clients concurrently)

    Example:
        .. code-block:: python

            import asyncio
            from pyrogram import Client, compose


            async def main():
                apps = [
                    Client("account1"),
                    Client("account2"),
                    Client("account3")
                ]

                ...

                await compose(apps)


            asyncio.run(main())

    """
    started = []

    if sequential:
        for c in clients:
            try:
                await c.start()
                started.append(c)
            except Exception:
                log.exception("Failed to start client %s", c.name)
    else:
        results = await asyncio.gather(
            *[c.start() for c in clients], return_exceptions=True
        )
        for c, result in zip(clients, results):
            if isinstance(result, Exception):
                log.exception("Failed to start client %s", c.name, exc_info=result)
            else:
                started.append(c)

    if not started:
        return

    await idle()

    if sequential:
        for c in started:
            try:
                await c.stop()
            except Exception:
                log.exception("Failed to stop client %s", c.name)
    else:
        results = await asyncio.gather(
            *[c.stop() for c in started], return_exceptions=True
        )
        for c, result in zip(started, results):
            if isinstance(result, Exception):
                log.exception("Failed to stop client %s", c.name, exc_info=result)
