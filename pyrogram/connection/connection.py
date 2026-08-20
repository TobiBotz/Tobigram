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
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, Type

from pyrogram.crypto.executor import get_crypto_executor
from .transport import TCP, TCPAbridged
from ..session.internals import DataCenter, get_dc_address

log = logging.getLogger(__name__)


TRANSPORT_ERRORS = {
    404: "auth key not found",
    429: "transport flood",
    444: "invalid DC"
}


def transport_error(packet: Optional[bytes]) -> Optional[str]:
    """Describe a packet too short to be a message, or None if it is one."""
    if packet is not None and len(packet) > 4:
        return None

    if not packet or len(packet) < 4:
        return "Connection closed by the server"

    error_code = -int.from_bytes(packet, "little", signed=True)

    return "Server sent transport error: {} ({})".format(
        error_code, TRANSPORT_ERRORS.get(error_code, "unknown error")
    )


class Connection:
    MAX_CONNECTION_ATTEMPTS = 3

    TRANSPORT_ERRORS = TRANSPORT_ERRORS

    def __init__(
        self,
        dc_id: int,
        test_mode: bool,
        ipv6: bool,
        proxy: dict,
        media: bool = False,
        protocol_factory: Type[TCP] = TCPAbridged,
        crypto_executor: Optional[ThreadPoolExecutor] = None,
        loop: Optional[asyncio.AbstractEventLoop] = None,
        server_address: Optional[str] = None,
        port: Optional[int] = None
    ):
        self.dc_id = dc_id
        self.test_mode = test_mode
        self.ipv6 = ipv6
        self.proxy = proxy
        self.media = media
        self.protocol_factory = protocol_factory
        self.crypto_executor = crypto_executor or get_crypto_executor()

        if server_address and port:
            self.address = (server_address, port)
        else:
            self.address = get_dc_address(dc_id, test_mode, ipv6, media)
        self.protocol: TCP = None

        if isinstance(loop, asyncio.AbstractEventLoop):
            self.loop = loop
        else:
            try:
                self.loop = asyncio.get_running_loop()
            except RuntimeError:
                self.loop = asyncio.get_event_loop_policy().get_event_loop()

    async def connect(self):
        last_error = None

        for i in range(Connection.MAX_CONNECTION_ATTEMPTS):
            self.protocol = self.protocol_factory(self.ipv6, self.proxy, self.crypto_executor, self.loop)

            try:
                log.info("Connecting...")
                await self.protocol.connect(self.address)
            except OSError as e:
                last_error = e
                log.warning("Unable to connect due to network issues: %s", e)
                await self.protocol.close()
                await asyncio.sleep(1)
            else:
                log.info("Connected! %s DC%s%s - IPv%s",
                         "Test" if self.test_mode else "Production",
                         self.dc_id,
                         " (media)" if self.media else "",
                         "6" if self.ipv6 else "4")
                break
        else:
            log.warning("Connection failed! Trying again...")
            raise ConnectionError(
                "Connection to DC{} at {}:{} failed: {}".format(
                    self.dc_id, self.address[0], self.address[1], last_error
                )
            ) from last_error

    async def close(self):
        if self.protocol is None:
            return
        async with self.protocol.lock:
            await self.protocol.close()
        log.info("Disconnected")

    async def send(self, data: bytes):
        await self.protocol.send(data)

    async def recv(self) -> Optional[bytes]:
        self.protocol.mid_message = False

        return await self.protocol.recv()
