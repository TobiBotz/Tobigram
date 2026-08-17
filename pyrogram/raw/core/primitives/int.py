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
from struct import Struct
from typing import Any

from ..tl_object import TLObject

_int_signed = Struct("<i").unpack
_int_unsigned = Struct("<I").unpack
_long_signed = Struct("<q").unpack
_long_unsigned = Struct("<Q").unpack


class Int(bytes, TLObject):
    SIZE = 4

    @staticmethod
    def read(data: BytesIO, signed: bool = True, *args: Any) -> int:
        if signed:
            return _int_signed(data.read(4))[0]

        return _int_unsigned(data.read(4))[0]

    def __new__(cls, value: int, signed: bool = True) -> bytes:  # type: ignore
        return value.to_bytes(cls.SIZE, "little", signed=signed)


class Long(Int):
    SIZE = 8

    @staticmethod
    def read(data: BytesIO, signed: bool = True, *args: Any) -> int:
        if signed:
            return _long_signed(data.read(8))[0]

        return _long_unsigned(data.read(8))[0]


class Int128(Int):
    SIZE = 16

    @staticmethod
    def read(data: BytesIO, signed: bool = True, *args: Any) -> int:
        return int.from_bytes(data.read(16), "little", signed=signed)


class Int256(Int):
    SIZE = 32

    @staticmethod
    def read(data: BytesIO, signed: bool = True, *args: Any) -> int:
        return int.from_bytes(data.read(32), "little", signed=signed)
