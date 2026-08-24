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

"""Examples import ``wzgram``; the library imports ``pyrogram``.

Both names reach the same module, so an example that says ``pyrogram`` still runs
and nothing here fails at import time. It drifts back one file at a time instead,
which is why this walks the tree rather than trusting a sweep.
"""

import ast
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

PYROGRAM_IMPORT = re.compile(
    r"(?m)^\s*(?:from pyrogram(?:\.[a-zA-Z_][a-zA-Z0-9_]*)* import\b|import pyrogram\s*$)"
)

# generated, or a generator of library code rather than of an example
SKIPPED = (
    ROOT / "docs" / "build",
    ROOT / "docs" / "source" / "telegram",
    ROOT / "docs" / "source" / "api" / "methods",
    ROOT / "docs" / "source" / "api" / "types",
    ROOT / "docs" / "source" / "api" / "bound-methods",
)

# repr() emits `pyrogram.types.X(...)`, so eval() of one needs that name bound;
# `import wzgram` binds the alias, not the name the repr uses
EXEMPT = {ROOT / "docs" / "source" / "topics" / "serializing.rst"}


def documentation_files():
    files = [
        p
        for p in ROOT.joinpath("docs", "source").rglob("*.rst")
        if not any(skip in p.parents for skip in SKIPPED)
    ]
    files.append(ROOT / "README.md")
    files.extend(ROOT.joinpath("compiler", "docs", "template").glob("*.rst"))

    return sorted(files)


def python_files():
    return sorted(
        p
        for p in ROOT.joinpath("pyrogram").rglob("*.py")
        if "raw" not in p.parts and "__pycache__" not in p.parts
    )


@pytest.mark.parametrize(
    "path", documentation_files(), ids=lambda p: str(p.relative_to(ROOT))
)
def test_documentation_examples_import_wzgram(path):
    if path in EXEMPT:
        pytest.skip("documented exception")

    found = PYROGRAM_IMPORT.findall(path.read_text(encoding="utf-8"))

    assert not found, f"{path.relative_to(ROOT)} still imports pyrogram in an example"


def test_docstring_examples_import_wzgram():
    """Only docstrings. Every other import in the tree is the library's own."""

    offenders = []
    scanned = 0

    for path in python_files():
        source = path.read_text(encoding="utf-8")

        if "pyrogram" not in source:
            continue

        for node in ast.walk(ast.parse(source)):
            if not isinstance(
                node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
            ):
                continue

            doc = ast.get_docstring(node, clean=False)

            if doc is None or "Example:" not in doc:
                continue

            scanned += 1

            if PYROGRAM_IMPORT.search(doc):
                name = getattr(node, "name", "<module>")
                offenders.append(f"{path.relative_to(ROOT)}:{name}")

    assert scanned > 300, f"only found {scanned} examples; the scan stopped working"
    assert not offenders, offenders


def test_the_library_itself_still_imports_pyrogram():
    """The package is pyrogram. A sweep that reaches the source breaks the build."""

    client = (ROOT / "pyrogram" / "client.py").read_text(encoding="utf-8")

    assert re.search(r"(?m)^from pyrogram import ", client), (
        "pyrogram/client.py must import pyrogram, not the alias"
    )

    for template in ROOT.joinpath("compiler", "methods", "templates").glob("*.j2"):
        body = template.read_text(encoding="utf-8")

        assert "from pyrogram import" in body, (
            f"{template.name} generates library code and must emit pyrogram imports"
        )
