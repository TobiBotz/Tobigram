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

import re
from datetime import datetime
from enum import Enum
from typing import Any

import orjson


def dumps(obj: Any, default: Any = None) -> str:
    return orjson.dumps(obj, default=default, option=orjson.OPT_INDENT_2).decode()


import pyrogram


def _public_attributes(instance: Object) -> dict[str, Any]:
    attrs = getattr(instance, "__dict__", None)
    if attrs is None:
        return {
            s: getattr(instance, s, None)
            for s in getattr(instance, "__slots__", ())
            if not s.startswith("_")
        }
    return {attribute: value for attribute, value in attrs.items() if not attribute.startswith("_")}


class Object:
    def __init__(self, client: pyrogram.Client | None = None):
        self._client = client

    def bind(self, client: pyrogram.Client):
        """Bind a Client instance to this and to all nested Pyrogram objects.

        Parameters:
            client (:obj:`~pyrogram.types.Client`):
                The Client instance to bind this object with. Useful to re-enable bound methods after serializing and
                deserializing Pyrogram objects with ``repr`` and ``eval``.
        """
        self._client = client

        for i in self.__dict__:
            o = getattr(self, i)

            if isinstance(o, Object):
                o.bind(client)

    @staticmethod
    def default(obj: Object):
        if isinstance(obj, bytes):
            return repr(obj)

        if isinstance(obj, re.Match):
            return repr(obj)

        if isinstance(obj, Enum):
            return str(obj)

        if isinstance(obj, datetime):
            return str(obj)

        attrs = getattr(obj, "__dict__", None)
        d: dict[str, Any] = {"_": obj.__class__.__name__}
        if attrs is not None:
            for k, v in attrs.items():
                if not k.startswith("_") and v is not None:
                    d[k] = "*********" if k == "phone_number" else v
        else:
            for s in getattr(obj, "__slots__", ()):
                v = getattr(obj, s, None)
                if v is not None:
                    d[s] = "*********" if s == "phone_number" else v

        return d

    def __str__(self) -> str:
        return dumps(self, default=Object.default)

    def __repr__(self) -> str:
        attrs = getattr(self, "__dict__", None)
        if attrs is None:
            attrs = {s: getattr(self, s, None) for s in getattr(self, "__slots__", ())}

        return "pyrogram.types.{}({})".format(
            self.__class__.__name__,
            ", ".join(
                f"{attr}={getattr(self, attr)!r}"
                for attr in filter(lambda x: not x.startswith("_"), attrs)
                if getattr(self, attr) is not None
            ),
        )

    def __eq__(self, other: object) -> bool:
        # Comparing attribute values alone makes an attribute-less type equal to anything,
        #  `None` and `42` included; `NotImplemented` leaves the verdict to the other operand.
        if type(other) is not type(self):
            return NotImplemented

        return _public_attributes(self) == _public_attributes(other)

    # Equality is by mutable attribute value (see `__eq__` above), so a stable hash across
    #  the object's lifetime cannot be guaranteed. Declared explicitly rather than relying on
    #  the implicit `__hash__ = None` Python already applies when `__eq__` is defined alone.
    __hash__ = None

    def __setstate__(self, state):
        for attr in state:
            obj = state[attr]

            # Maybe a better alternative would be https://docs.python.org/3/library/inspect.html#inspect.signature
            if isinstance(obj, tuple) and len(obj) == 2 and obj[0] == "dt":
                state[attr] = datetime.fromtimestamp(obj[1])

        self.__dict__ = state

    def __getstate__(self):
        state = self.__dict__.copy()
        state.pop("_client", None)

        for attr in state:
            obj = state[attr]

            if isinstance(obj, datetime):
                state[attr] = ("dt", obj.timestamp())

        return state
