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

"""The schema is imported on first use, not all at once.

`pyrogram/raw` is several thousand one-class modules and a client touches a
handful of them. Importing every one cost 33 MiB of resident memory and two
seconds of start-up in a process that never used the rest.

Nothing here fails at runtime if the laziness is lost — every name still
resolves, the import is simply eager again — so these count modules rather than
check that an attribute exists.
"""

import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

# what an import legitimately pulls: the update types the dispatcher maps, and the
# constructors the enums and filters hold by value. A ceiling and a share of the
# schema, so the guard keeps meaning as the schema grows.
BUDGET = 250
SHARE = 0.1


def run(code):
    result = subprocess.run(
        [sys.executable, "-c", textwrap.dedent(code)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )

    assert result.returncode == 0, result.stderr

    return result.stdout.strip().splitlines()


def loaded(extra=""):
    return int(
        run(
            f"""
            import sys
            import pyrogram
            {extra}
            print(len([
                m for m in sys.modules
                if m.startswith(("pyrogram.raw.types.", "pyrogram.raw.functions.",
                                 "pyrogram.raw.base."))
            ]))
            """
        )[-1]
    )


def test_importing_pyrogram_loads_almost_none_of_the_schema():
    count = loaded()
    total = len(list((ROOT / "pyrogram" / "raw").rglob("*.py")))

    assert count < BUDGET and count < total * SHARE, (
        f"importing pyrogram pulled {count} of {total} schema modules; the packages "
        f"under pyrogram/raw are meant to resolve names on first use"
    )


def test_the_schema_is_still_large():
    """A budget is worthless if there is nothing to be under it."""

    total = len(list((ROOT / "pyrogram" / "raw" / "types").rglob("*.py")))

    assert total > 1000, f"only {total} type modules; run poe api"


def test_a_name_loads_only_its_own_module():
    before, after = run(
        """
        import sys
        import pyrogram
        from pyrogram import raw

        def n():
            return len([m for m in sys.modules if m.startswith("pyrogram.raw.types.")])

        print(n())
        raw.types.Message
        print(n())
        """
    )

    assert int(after) - int(before) == 1


@pytest.mark.parametrize(
    "expression",
    [
        "raw.types.Message",
        "raw.functions.messages.SendMessage",
        "raw.base.Message",
        "raw.types.messages.Messages",
    ],
)
def test_every_kind_of_name_still_resolves(expression):
    assert run(
        f"""
        from pyrogram import raw
        print({expression} is not None)
        """
    ) == ["True"]


def test_a_name_the_schema_does_not_have_raises_attribute_error():
    assert run(
        """
        from pyrogram import raw

        try:
            raw.types.NoSuchConstructor
        except AttributeError as e:
            print("AttributeError", "NoSuchConstructor" in str(e))
        """
    ) == ["AttributeError True"]


def test_a_star_import_still_works():
    """__all__ is what makes one possible once the module imports lazily."""

    assert run(
        """
        ns = {}
        exec("from pyrogram.raw.types import *", ns)
        print(ns["Message"].__name__, len(ns) > 1000)
        """
    ) == ["Message True"]


def test_dir_lists_the_whole_package():
    assert run(
        """
        from pyrogram import raw
        names = dir(raw.types)
        print("Message" in names, len(names) > 1000)
        """
    ) == ["True True"]


class TestObjects:
    """The constructor id map resolves an id when it arrives, not before."""

    def test_a_lookup_imports_one_module(self):
        before, after, name = run(
            """
            import sys
            from pyrogram import raw

            def n():
                return len([m for m in sys.modules if m.startswith("pyrogram.raw.types.")])

            print(n())
            cls = raw.objects[0x7600B9D3]
            print(n())
            print(cls.__name__)
            """
        )

        assert int(after) - int(before) == 1
        assert name == "Message"

    def test_it_still_looks_like_the_whole_map(self):
        assert run(
            """
            from pyrogram import raw
            from pyrogram.raw.all import objects

            print(len(raw.objects) == len(objects))
            print(0x7600B9D3 in raw.objects)
            print(raw.objects.get(0xdeadbeef) is None)
            print(len(list(iter(raw.objects))) == len(objects))
            """
        ) == ["True", "True", "True", "True"]

    def test_an_unknown_id_raises_key_error(self):
        assert run(
            """
            from pyrogram import raw

            try:
                raw.objects[0xdeadbeef]
            except KeyError:
                print("KeyError")
            """
        ) == ["KeyError"]

    def test_a_class_put_in_the_map_by_hand_still_works(self):
        """all.objects was a live dict of classes before this became lazy."""

        assert run(
            """
            from io import BytesIO
            from pyrogram.raw.all import objects
            from pyrogram.raw.core import TLObject

            class Probe:
                @staticmethod
                def read(b, *args):
                    return "ok"

            objects[0x7E571234] = Probe
            print(TLObject.read(BytesIO((0x7E571234).to_bytes(4, "little"))))
            """
        ) == ["ok"]


def test_the_compiler_emits_the_lazy_form():
    """poe api regenerates these packages, so the shape has to come from there."""

    source = (ROOT / "compiler" / "api" / "compiler.py").read_text(encoding="utf-8")

    assert "def __getattr__(name):" in source
    assert "_names" in source and "_subpackages" in source
    assert "from .{snake(module)} import" not in source, (
        "the compiler writes eager imports again"
    )
