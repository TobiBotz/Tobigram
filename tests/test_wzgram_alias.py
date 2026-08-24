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

"""``import wzgram`` must be ``import pyrogram``, not a second copy of it.

Anything that imports the tree twice hands back a second set of classes, and a
``Message`` parsed by one then fails ``isinstance`` against the other — which
shows up as a filter that never matches rather than as an import error.

Import order is what decides that, so the cases that depend on it run in their
own interpreter. The rest share one, because starting a second costs a second.
"""

import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

SYMBOLS = [
    ("", "Client"),
    (".types", "Message"),
    (".enums", "ParseMode"),
    (".errors", "FloodWait"),
    (".filters", "command"),
    (".handlers", "MessageHandler"),
    (".raw.functions.messages", "SendMessage"),
    (".raw.types", "PeerUser"),
]


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


@pytest.fixture(scope="module")
def report():
    imports = "\n".join(
        f"from wzgram{module} import {name} as a{i}\n"
        f"from pyrogram{module} import {name} as b{i}\n"
        f"print({name!r}, a{i} is b{i})"
        for i, (module, name) in enumerate(SYMBOLS)
    )

    lines = run(
        f"""
        import sys
        import pyrogram
        import wzgram
        import wzgram.raw.functions.messages

        print('module', wzgram is pyrogram)
        print('version', wzgram.__version__ == pyrogram.__version__)
        print('canonical', wzgram.Client.__module__ == 'pyrogram.client')

        names = [k for k in sys.modules if k == 'wzgram' or k.startswith('wzgram.')]
        print('registered', len(names) > 1 and all(
            sys.modules[k] is sys.modules['pyrogram' + k[len('wzgram'):]]
            for k in names
        ))

        instance = pyrogram.Client('x', api_id=1, api_hash='a', in_memory=True)
        print('isinstance', isinstance(instance, wzgram.Client))

        star_a, star_b = {{}}, {{}}
        exec('from wzgram import *', star_a)
        exec('from pyrogram import *', star_b)
        del star_a['__builtins__'], star_b['__builtins__']
        print('star', star_a.keys() == star_b.keys() and all(
            star_a[k] is star_b[k] for k in star_a
        ))

{textwrap.indent(imports, " " * 8)}
        """
    )

    return dict(line.split(" ", 1) for line in lines)


@pytest.mark.parametrize(
    "check",
    ["module", "version", "canonical", "registered", "isinstance", "star"],
)
def test_the_two_names_are_one_module(report, check):
    assert report[check] == "True"


@pytest.mark.parametrize("name", [name for _, name in SYMBOLS])
def test_every_symbol_is_the_same_object(report, name):
    assert report[name] == "True"


def test_the_alias_works_when_it_is_imported_first():
    """The finder has to be installed before anything reaches for a submodule."""

    assert run(
        """
        import wzgram.types as t
        import pyrogram
        print('deep', t is pyrogram.types)
        """
    ) == ["deep True"]


def test_the_alias_works_when_pyrogram_is_imported_first():
    assert run(
        """
        import pyrogram.types
        import wzgram.types as t
        print('deep', t is pyrogram.types)
        """
    ) == ["deep True"]


def test_the_alias_ships_in_the_wheel():
    packages = (ROOT / "pyproject.toml").read_text(encoding="utf-8")

    assert 'packages = ["pyrogram", "wzgram"]' in packages, (
        "the alias is importable from a checkout whether or not it is packaged"
    )
