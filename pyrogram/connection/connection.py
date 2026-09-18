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
import logging
from concurrent.futures import ThreadPoolExecutor

from pyrogram import utils
from pyrogram.crypto.executor import get_crypto_executor

from ..session.internals import get_dc_address
from .proxy import Proxy, normalize_proxy, uses_random_padding
from .transport import TCP, TCPAbridged, TCPIntermediatePadded

log = logging.getLogger(__name__)

# tdesktop's protocolDcId (session_private.cpp:254-265): the media cluster
# is the negated dc id, test-mode servers get a further +10000 shift. Only
# the WEB proxy scheme embeds this (TCP._connect_via_web_proxy's nonce);
# other transports address the DC by IP and never see it.
_TEST_MODE_DC_ID_SHIFT = 10000


def transport_class_for(proxy: Proxy | None, *, default: type[TCP] = TCPAbridged) -> type[TCP]:
    """The transport a proxy's secret requires, or `default` when it requires none.

    A dd- or ee-prefixed secret asks for random padding, so the secret decides the
    framing and the caller does not: TDLib builds the same choice into its
    obfuscated transport's constructor.
    """
    if uses_random_padding(proxy):
        return TCPIntermediatePadded

    return default


def _protocol_dc_id(dc_id: int, test_mode: bool, media: bool) -> int:
    value = dc_id + (_TEST_MODE_DC_ID_SHIFT if test_mode else 0)
    return -value if media else value


TRANSPORT_ERRORS = {404: "auth key not found", 429: "transport flood", 444: "invalid DC"}


def transport_error(packet: bytes | None) -> str | None:
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
        test_mode: bool = False,
        ipv6: bool = False,
        proxy: dict | str | Proxy | None = None,
        media: bool = False,
        protocol_factory: type[TCP] = TCPAbridged,
        crypto_executor: ThreadPoolExecutor | None = None,
        loop: asyncio.AbstractEventLoop | None = None,
        server_address: str | None = None,
        port: int | None = None,
    ):
        self.dc_id = dc_id
        self.test_mode = test_mode
        self.ipv6 = ipv6
        self.proxy = normalize_proxy(proxy)
        self.media = media
        self.protocol_factory = transport_class_for(self.proxy, default=protocol_factory)

        if self.protocol_factory is not protocol_factory:
            log.debug(
                "Proxy secret asks for random padding, so %s frames this connection",
                self.protocol_factory.__name__,
            )

        self.crypto_executor = crypto_executor or get_crypto_executor()
        self._protocol_dc_id = _protocol_dc_id(dc_id, test_mode, media)

        if server_address and port:
            self.address = (server_address, port)
        else:
            self.address = get_dc_address(dc_id, test_mode, ipv6, media)
        self.protocol: TCP = None

        if isinstance(loop, asyncio.AbstractEventLoop):
            self.loop = loop
        else:
            self.loop = utils.get_event_loop()

    async def connect(self):
        last_error = None

        for i in range(Connection.MAX_CONNECTION_ATTEMPTS):
            try:
                self.protocol = self.protocol_factory(
                    self.ipv6,
                    self.proxy,
                    self.crypto_executor,
                    self.loop,
                    dc_id=self._protocol_dc_id,
                )
            except TypeError:
                self.protocol = self.protocol_factory(
                    self.ipv6, self.proxy, self.crypto_executor, self.loop
                )

            try:
                log.info("Connecting...")
                await self.protocol.connect(self.address)
            except OSError as e:
                last_error = e
                log.warning("Unable to connect due to network issues: %s", e)
                await self.protocol.close()
                await asyncio.sleep(1)
            else:
                log.info(
                    "Connected! %s DC%s%s - IPv%s",
                    "Test" if self.test_mode else "Production",
                    self.dc_id,
                    " (media)" if self.media else "",
                    "6" if self.ipv6 else "4",
                )
                break
        else:
            log.warning("Connection failed! Trying again...")
            raise ConnectionError(
                f"Connection to DC{self.dc_id} at {self.address[0]}:{self.address[1]} failed: {last_error}"
            ) from last_error

    async def close(self):
        if self.protocol is None:
            return
        async with self.protocol.lock:
            await self.protocol.close()
        log.info("Disconnected")

    async def send(self, data: bytes):
        await self.protocol.send(data)

    async def recv(self) -> bytes | None:
        self.protocol.mid_message = False

        return await self.protocol.recv()
