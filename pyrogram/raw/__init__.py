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

from importlib import import_module

from . import core
from .core.tl_object import objects


def __getattr__(name):
    """Load types, functions or base on first use.

    Each is a package of thousands of one-class modules, and a client touches a
    handful of them.
    """

    if name in ("types", "functions", "base"):
        value = import_module("." + name, __name__)
        globals()[name] = value

        return value

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
