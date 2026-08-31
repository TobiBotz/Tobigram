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
from typing import cast, Union, Any

from .int import Int, Long
from ..list import List
from ..tl_object import TLObject


class Vector(bytes, TLObject):
    ID = 0x1CB5C415

    # Method added to handle the special case when a query returns a bare Vector (of Ints);
    # i.e., RpcResult body starts with 0x1cb5c415 (Vector Id) - e.g., messages.GetMessagesViews.
    @staticmethod
    def read_bare(b: BytesIO, size: int) -> Union[int, Any]:
        if size == 4:
            return Int.read(b)

        if size == 8:
            return Long.read(b)

        return TLObject.read(b)

    @classmethod
    def read(cls, data: BytesIO, t: Any = None, *args: Any) -> List:
        count = Int.read(data)

        if t is not None:
            read = t.read
            return List([read(data) for _ in range(count)])

        if not count:
            return List()

        pos = data.tell()

        try:
            return List([TLObject.read(data) for _ in range(count)])
        except Exception:
            data.seek(pos)

        size = (data.seek(0, 2) - pos) / count
        data.seek(pos)

        if size == 4:
            read = Int.read
        elif size == 8:
            read = Long.read
        else:
            read = TLObject.read

        return List([read(data) for _ in range(count)])

    def __new__(cls, value: list, t: Any = None) -> bytes:  # type: ignore
        return b"".join(
            [Int(cls.ID, False), Int(len(value))]
            + [cast(bytes, t(i)) if t else i.write() for i in value]
        )
