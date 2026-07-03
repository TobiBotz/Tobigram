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

from io import BytesIO

import warpcrypto
from warpcrypto import kdf

from pyrogram.errors import SecurityCheckMismatch
from pyrogram.raw.core import Message


def pack(message: Message, salt: int, session_id: bytes, auth_key: bytes, auth_key_id: bytes) -> bytes:
    data = message.write()
    msg_id = int.from_bytes(data[0:8], "little", signed=True)
    seq_no = int.from_bytes(data[8:12], "little", signed=False)
    body = data[16:]
    return warpcrypto.pack_message(msg_id, seq_no, body, salt, session_id, auth_key, auth_key_id)


def unpack(
    b: BytesIO,
    session_id: bytes,
    auth_key: bytes,
    auth_key_id: bytes
) -> Message:
    packed = b.read()
    msg_id, seq_no, length, body_bytes, total_len = warpcrypto.unpack_message(
        packed, session_id, auth_key, auth_key_id
    )

    padding = total_len - 16 - length
    SecurityCheckMismatch.check(12 <= padding <= 1024, "12 <= len(padding) <= 1024")
    SecurityCheckMismatch.check(total_len % 4 == 0, "len(data) % 4 == 0")

    buf = BytesIO(body_bytes)

    try:
        message = Message.read(buf)
    except KeyError as e:
        if e.args[0] == 0:
            raise ConnectionError(f"Received empty data. Check your internet connection.")

        left = body_bytes.hex()
        left = [left[i:i + 64] for i in range(0, len(left), 64)]
        left = [[left[i:i + 8] for i in range(0, len(left), 8)] for left in left]
        left = "\n".join(" ".join(x for x in left) for left in left)

        raise ValueError(f"The server sent an unknown constructor: {hex(e.args[0])}\n{left}")

    SecurityCheckMismatch.check(message.msg_id % 2 != 0, "message.msg_id % 2 != 0")

    return message
