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

import importlib
from io import BytesIO
from json import dumps
from struct import Struct
from typing import List, Any, Union, Dict

from ..all import objects as _paths

_constructor = Struct("<I").unpack


class _Objects(dict):
    """Constructor id to class, resolved the first time that id arrives.

    ``all.objects`` maps every id in the schema to a dotted path. Walking it at
    import time to build a table of classes pulled in every one of the several
    thousand one-class modules the schema generates, for a session that reads a
    few dozen entries out of it.

    ``__missing__`` raises ``KeyError`` for an id the schema does not know, which
    is what ``read`` already handles.
    """

    def __missing__(self, key: int) -> Any:
        path = _paths[key]

        # a class rather than a path means someone put one in all.objects, which
        # was a live dict of classes before this became lazy
        if isinstance(path, str):
            module_path, class_name = path.rsplit(".", 1)
            value = getattr(importlib.import_module(module_path), class_name)
        else:
            value = path

        self[key] = value

        return value

    def __contains__(self, key: object) -> bool:
        return key in _paths

    def __iter__(self):
        return iter(_paths)

    def __len__(self) -> int:
        return len(_paths)

    def keys(self):
        return _paths.keys()

    def get(self, key, default=None):
        return self[key] if key in _paths else default


objects = _Objects()

_legacy_objects: Dict[int, str] = {
    0xf2355507: "pyrogram.raw.types.ChannelFull",
    0xc9d31138: "pyrogram.raw.types.ChatFull",
    0x31774388: "pyrogram.raw.types.User",
}


class TLObject:
    __slots__: List[str] = []

    QUALNAME = "Base"

    @classmethod
    def read(cls, b: BytesIO, *args: Any) -> Any:
        constructor_id = _constructor(b.read(4))[0]

        try:
            obj_class = objects[constructor_id]
        except KeyError as e:
            path = _legacy_objects.get(constructor_id)

            if path is None:
                raise KeyError(constructor_id) from e

            module_path, class_name = path.rsplit(".", 1)
            obj_class = getattr(importlib.import_module(module_path), class_name)

        if args:
            return obj_class.read(b, *args)

        return obj_class.read(b)

    def write(self, *args: Any) -> bytes:
        pass

    @staticmethod
    def default(obj: "TLObject") -> Union[str, Dict[str, str]]:
        if isinstance(obj, bytes):
            return repr(obj)

        return {
            "_": obj.QUALNAME,
            **{
                attr: getattr(obj, attr)
                for attr in obj.__slots__
                if getattr(obj, attr) is not None
            }
        }

    def __str__(self) -> str:
        return dumps(self, indent=4, default=TLObject.default, ensure_ascii=False)

    def __repr__(self) -> str:
        if not hasattr(self, "QUALNAME"):
            return repr(self)

        return "pyrogram.raw.{}({})".format(
            self.QUALNAME,
            ", ".join(
                f"{attr}={repr(getattr(self, attr))}"
                for attr in self.__slots__
                if getattr(self, attr) is not None
            )
        )

    def __eq__(self, other: Any) -> bool:
        for attr in self.__slots__:
            try:
                if getattr(self, attr) != getattr(other, attr):
                    return False
            except AttributeError:
                return False

        return True

    def __bool__(self) -> bool:
        return True

    def __len__(self) -> int:
        return len(self.write())

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        pass
