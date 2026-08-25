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

"""Every public client method, against what it says about itself.

The Bot API coverage gate runs this axis too, but only for the hundred methods the
manifest maps to a spec entry. Two thirds of the surface is never checked, and that
is where `send_location` and `send_venue` sat for however long with a docstring the
interpreter could not see.

`data_undocumented_params.json` is a frozen high-water mark, the same idea as the
manifest's `pending:` list: it may shrink, never grow. Documenting a parameter and
leaving it listed here fails just as loudly as adding a new undocumented one, so the
file cannot rot into an exemption.
"""

import ast
import inspect
import json
import textwrap
from pathlib import Path

import pytest

from pyrogram.methods import Methods

ROOT = Path(__file__).resolve().parents[1]
FROZEN = json.loads(
    (ROOT / "tests" / "data_undocumented_params.json").read_text(encoding="utf-8")
)

IGNORE = {"self", "args", "kwargs"}

# a decorator returns a decorator; saying so in a Returns: block is noise, and all
# twenty-odd of them agree on that
DECORATORS = tuple(n for n in dir(Methods) if n.startswith("on_"))


def public_methods():
    for name in sorted(dir(Methods)):
        if name.startswith("_"):
            continue

        fn = getattr(Methods, name, None)

        if callable(fn):
            yield name, fn


def docstring(fn):
    """The docstring as the file has it, not as the interpreter dedents it."""

    try:
        source = textwrap.dedent(inspect.getsource(fn))
    except OSError:
        return None

    return ast.get_docstring(ast.parse(source).body[0], clean=False)


def documented(doc):
    """The parameters the reST ``Parameters:`` block claims exist.

    ``Other Parameters:`` describes what a progress callback is handed, not what the
    method takes, and it ends the block — a parameter documented below it is
    documented in the wrong place.
    """

    import re

    section = re.compile(r"^\s{4}(\w[\w ]*):\s*$")
    parameter = re.compile(r"^\s{8}(\w+(?:\s*,\s*\w+)*)\s*\(")

    found, inside = set(), False

    for line in (doc or "").splitlines():
        heading = section.match(line)

        if heading:
            inside = heading.group(1) == "Parameters"
            continue

        if inside:
            hit = parameter.match(line)

            if hit:
                found.update(n.strip() for n in hit.group(1).split(","))

    return found


METHODS = list(public_methods())


@pytest.mark.parametrize("name,fn", METHODS, ids=[n for n, _ in METHODS])
def test_every_method_has_a_docstring_the_interpreter_can_see(name, fn):
    """A string that is not the first statement is not a docstring."""

    assert docstring(fn), (
        f"{name} has no docstring, or has one the interpreter cannot see because "
        f"another statement comes first"
    )


@pytest.mark.parametrize("name,fn", METHODS, ids=[n for n, _ in METHODS])
def test_every_method_says_what_it_returns(name, fn):
    doc = docstring(fn) or ""

    if name in DECORATORS:
        pytest.skip("a decorator returns a decorator")

    assert "Returns:" in doc or "Yields:" in doc, f"{name} says nothing about its result"


@pytest.mark.parametrize("name,fn", METHODS, ids=[n for n, _ in METHODS])
def test_no_method_documents_a_parameter_it_does_not_accept(name, fn):
    """This one has no frozen list. A phantom parameter is always a defect."""

    real = {p for p in inspect.signature(fn).parameters if p not in IGNORE}
    phantom = documented(docstring(fn)) - real

    assert not phantom, f"{name} documents {', '.join(sorted(phantom))}, which it does not accept"


@pytest.mark.parametrize("name,fn", METHODS, ids=[n for n, _ in METHODS])
def test_undocumented_parameters_only_shrink(name, fn):
    real = {p for p in inspect.signature(fn).parameters if p not in IGNORE}

    if not real:
        return

    doc = docstring(fn)

    assert doc is not None

    missing = real - documented(doc)
    frozen = set(FROZEN.get(name, ()))

    new = missing - frozen

    assert not new, (
        f"{name} accepts {', '.join(sorted(new))} without documenting "
        f"{'them' if len(new) > 1 else 'it'}"
    )

    closed = frozen - missing

    assert not closed, (
        f"{name} now documents {', '.join(sorted(closed))}; drop "
        f"{'them' if len(closed) > 1 else 'it'} from "
        f"tests/data_undocumented_params.json so the list keeps shrinking"
    )


def test_the_frozen_list_names_real_methods():
    """A rename would otherwise leave an entry that exempts nothing."""

    known = {name for name, _ in METHODS}
    stale = sorted(set(FROZEN) - known)

    assert not stale, f"tests/data_undocumented_params.json names {stale}"
