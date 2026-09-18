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

import asyncio
import random
import time

import pyrogram
from pyrogram import raw


class Ping:
    async def ping(self: pyrogram.Client, attempts: int = 1) -> float:
        """Measure the round-trip network latency to the connected Telegram data center.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            attempts (``int``, *optional*):
                The number of ping attempts to measure. If greater than 1, the average latency
                across all attempts is returned. Defaults to 1.

        Returns:
            ``float``: The round-trip time (RTT) latency in milliseconds, rounded to 2 decimal places.

        Example:
            .. code-block:: python

                # Single ping measurement
                latency = await app.ping()
                print(f"Latency: {latency} ms")

                # Average of 3 pings
                avg_latency = await app.ping(attempts=3)
                print(f"Average latency: {avg_latency} ms")
        """
        attempts = max(1, attempts)
        latencies: list[float] = []

        for i in range(attempts):
            ping_id = random.randint(1, 2**63 - 1)
            t0 = time.perf_counter()
            try:
                await self.invoke(raw.functions.Ping(ping_id=ping_id))
            except Exception:
                await self.get_me()
            elapsed_ms = (time.perf_counter() - t0) * 1000
            latencies.append(elapsed_ms)

            if i < attempts - 1:
                await asyncio.sleep(0.02)

        return round(sum(latencies) / len(latencies), 2)
