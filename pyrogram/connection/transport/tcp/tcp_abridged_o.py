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

from pyrogram.crypto import aes

from .tcp import TCP, finalize_obfuscated2_tag, generate_obfuscated2_nonce

log = logging.getLogger(__name__)


class TCPAbridgedO(TCP):
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
        self.stream_lock = asyncio.Lock()

    async def connect(self, address: tuple):
        await super().connect(address)

        nonce = generate_obfuscated2_nonce()
        nonce[56] = nonce[57] = nonce[58] = nonce[59] = 0xEF

        temp = bytearray(nonce[55:7:-1])

        self.encrypt = (bytes(nonce[8:40]), nonce[40:56], bytearray(1))
        self.decrypt = (bytes(temp[0:32]), temp[32:48], bytearray(1))

        nonce[56:64] = finalize_obfuscated2_tag(nonce, self.encrypt)

        await super().send(nonce)

    async def send(self, data: bytes, *args):
        length = len(data) // 4
        data = (bytes([length]) if length <= 126 else b"\x7f" + length.to_bytes(3, "little")) + data

        async with self.stream_lock:
            encrypted = aes.ctr256_encrypt(data, *self.encrypt)
            await super().send(encrypted)

    async def recv(self, length: int = 0) -> bytes | None:
        length = await super().recv(1)

        if length is None:
            return None

        length = aes.ctr256_decrypt(length, *self.decrypt)

        if length == b"\x7f":
            length = await super().recv(3)

            if length is None:
                return None

            length = aes.ctr256_decrypt(length, *self.decrypt)

        data = await super().recv(int.from_bytes(length, "little") * 4)

        if data is None:
            return None

        return aes.ctr256_decrypt(data, *self.decrypt)
