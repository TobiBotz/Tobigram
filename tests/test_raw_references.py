"""Verify every ``raw.*`` name referenced by hand-written code exists.

Raw function and type names are PascalCase. A camelCase typo
(``messages.getPollResults`` instead of ``messages.GetPollResults``) parses
fine and only blows up as an ``AttributeError`` the first time the method is
actually called, so it survives review and reaches users.
"""

import ast
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from pyrogram import raw

PACKAGE = ROOT / "pyrogram"
GENERATED = PACKAGE / "raw"


def dotted(node: ast.Attribute):
    parts = []

    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value

    if not isinstance(node, ast.Name):
        return None

    parts.append(node.id)

    return list(reversed(parts))


def raw_references():
    for path in sorted(PACKAGE.rglob("*.py")):
        if GENERATED in path.parents:
            continue

        tree = ast.parse(path.read_text(encoding="utf-8"))

        for node in ast.walk(tree):
            if not isinstance(node, ast.Attribute):
                continue

            parts = dotted(node)

            if parts and parts[0] == "raw" and len(parts) >= 3:
                yield path.relative_to(ROOT), node.lineno, parts[1:]


@pytest.mark.parametrize(
    "path,lineno,parts",
    list(raw_references()),
    ids=lambda v: str(v) if not isinstance(v, list) else ".".join(v)
)
def test_raw_reference_resolves(path, lineno, parts):
    obj = raw

    for part in parts:
        obj = getattr(obj, part, None)

        assert obj is not None, f"{path}:{lineno} references raw.{'.'.join(parts)}, which does not exist"
