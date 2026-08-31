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

import os
import random
import logging
import asyncio
from struct import pack, unpack
from typing import Optional

from .tcp import TCP

log = logging.getLogger(__name__)


def strip_padding(payload: bytes) -> bytes:
    if len(payload) >= 20 and int.from_bytes(payload[:8], "little") == 0:
        return payload[:20 + int.from_bytes(payload[16:20], "little")]

    return payload[:len(payload) - (len(payload) - 8) % 16]


class TCPPaddedIntermediate(TCP):
    def __init__(self, ipv6: bool, proxy: dict, crypto_executor=None, loop: Optional[asyncio.AbstractEventLoop] = None):
        super().__init__(ipv6, proxy, crypto_executor, loop)

    async def connect(self, address: tuple):
        await super().connect(address)
        await super().send(b"\xdd" * 4)

    async def send(self, data: bytes, *args):
        padding = os.urandom(random.randint(0, 15))
        await super().send(pack("<i", len(data) + len(padding)) + data + padding)

    async def recv(self, length: int = 0) -> Optional[bytes]:
        length = await super().recv(4)

        if length is None:
            return None

        total_len = unpack("<i", length)[0]
        payload_plus_padding = await super().recv(total_len)

        if payload_plus_padding is None:
            return None

        return strip_padding(payload_plus_padding)
