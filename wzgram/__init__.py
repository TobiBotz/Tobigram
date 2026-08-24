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

"""``wzgram`` under its own name.

The package is and stays ``pyrogram``, so that wzgram is a drop-in replacement
and every import written against Pyrogram keeps working. This module makes the
distribution name importable too, by *being* ``pyrogram`` rather than wrapping
it: there is one set of classes, and ``wzgram.types.Message is
pyrogram.types.Message``.
"""

import importlib
import importlib.util
import sys

import pyrogram


class WzgramFinder:
    """Serves ``wzgram.X`` from the already-imported ``pyrogram.X``.

    Aliasing the top-level name alone is not enough. Once ``sys.modules["wzgram"]``
    is ``pyrogram``, its ``__path__`` points into ``pyrogram/``, so
    ``import wzgram.types`` would fall through to the path finder, execute
    ``pyrogram/types/__init__.py`` a second time under a second name, and hand
    back a second ``Message`` class that fails ``isinstance`` against the one
    every parser produces.

    A meta path finder runs before the path finder, so this intercepts the name
    first and returns the module that already exists.
    """

    PREFIX = "wzgram."

    def find_spec(self, fullname, path=None, target=None):
        if not fullname.startswith(self.PREFIX):
            return None

        return importlib.util.spec_from_loader(fullname, self)

    def create_module(self, spec):
        return importlib.import_module("pyrogram." + spec.name[len(self.PREFIX):])

    def exec_module(self, module):
        pass


if not any(isinstance(finder, WzgramFinder) for finder in sys.meta_path):
    sys.meta_path.insert(0, WzgramFinder())

sys.modules[__name__] = pyrogram
