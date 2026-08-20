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
from pyrogram import raw

log = logging.getLogger(__name__)


class Terminate:
    async def terminate(
        self: "pyrogram.Client",
    ):
        """Terminate the client by shutting down workers.

        This method does the opposite of :meth:`~pyrogram.Client.initialize`.
        It will stop the dispatcher and shut down updates and download workers.

        Raises:
            ConnectionError: In case you try to terminate a client that is already terminated.
        """
        if not self.is_initialized:
            raise ConnectionError("Client is already terminated")

        await self.listeners.close()

        if self.takeout_id:
            await self.invoke(raw.functions.account.FinishTakeoutSession())
            log.info("Takeout session %s finished", self.takeout_id)

        await self.storage.save()
        await self.dispatcher.stop()

        self.media_pool_reaper_event.set()

        if self.media_pool_reaper_task is not None:
            try:
                await self.media_pool_reaper_task
            except Exception:
                log.exception("Error stopping media pool reaper")

            self.media_pool_reaper_task = None

        self.media_pool_reaper_event.clear()

        for session in [
            *self.sessions.values(),
            *self.media_sessions.values(),
            *(s for pool in self.media_session_pools.values() for s in pool),
        ]:
            try:
                await session.stop()
            except Exception:
                log.exception("Error stopping session")

        self.sessions.clear()
        self.media_sessions.clear()
        self.media_session_pools.clear()

        self.updates_watchdog_event.set()

        if self.updates_watchdog_task is not None:
            try:
                await self.updates_watchdog_task
            except Exception:
                log.exception("Error stopping updates watchdog")

            self.updates_watchdog_task = None

        self.updates_watchdog_event.clear()

        self.is_initialized = False

        if self.rate_limiter is not None:
            await self.rate_limiter.close()
