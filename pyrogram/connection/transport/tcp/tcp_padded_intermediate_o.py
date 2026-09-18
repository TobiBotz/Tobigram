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
import os
import random
from struct import pack, unpack

from pyrogram.crypto import aes

from .tcp import TCP, finalize_obfuscated2_tag, generate_obfuscated2_nonce
from .tcp_padded_intermediate import strip_padding

log = logging.getLogger(__name__)


class TCPPaddedIntermediateO(TCP):
    def __init__(
        self,
        ipv6: bool = False,
        proxy=None,
        crypto_executor=None,
        loop: asyncio.AbstractEventLoop | None = None,
        dc_id: int | None = None,
    ):
        super().__init__(ipv6, proxy, crypto_executor, loop, dc_id=dc_id)

        self.encrypt = None
        self.decrypt = None

    async def connect(self, address: tuple):
        await super().connect(address)

        nonce = generate_obfuscated2_nonce()
        nonce[56] = nonce[57] = nonce[58] = nonce[59] = 0xDD

        temp = bytearray(nonce[55:7:-1])

        self.encrypt = (bytes(nonce[8:40]), nonce[40:56], bytearray(1))
        self.decrypt = (bytes(temp[0:32]), temp[32:48], bytearray(1))

        nonce[56:64] = finalize_obfuscated2_tag(nonce, self.encrypt)

        await super().send(nonce)

    async def send(self, data: bytes, *args):
        padding = os.urandom(random.randint(0, 15))
        await super().send(
            aes.ctr256_encrypt(pack("<i", len(data) + len(padding)) + data + padding, *self.encrypt)
        )

    async def recv(self, length: int = 0) -> bytes | None:
        length = await super().recv(4)

        if length is None:
            return None

        length = aes.ctr256_decrypt(length, *self.decrypt)
        total_len = unpack("<i", length)[0]

        data = await super().recv(total_len)

        if data is None:
            return None

        data = aes.ctr256_decrypt(data, *self.decrypt)

        return strip_padding(data)
