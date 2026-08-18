import ast
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "compiler" / "methods"))

from compiler import parse_tl_functions

PACKAGE = ROOT / "pyrogram"
GENERATED = PACKAGE / "raw"
TL_SOURCE = ROOT / "compiler" / "api" / "source" / "main_api.tl"

TL = parse_tl_functions(TL_SOURCE)

# TL scalars we can recognise in a literal argument
SCALARS = {"int", "long", "double", "string", "bytes", "Bool", "true", "int128", "int256"}
COMPATIBLE = {
    "int": {"int", "long", "true", "Bool"},
    "long": {"int", "long"},
    "double": {"double", "int", "long"},
    "string": {"string"},
    "bytes": {"bytes"},
    "Bool": {"Bool", "true"},
    "true": {"Bool", "true"},
}


def tl_name(parts):
    """raw.types.InputMediaPoll -> inputMediaPoll, raw.functions.messages.X -> messages.x"""
    namespace, name = parts[:-1], parts[-1]

    return ".".join([*namespace, name[:1].lower() + name[1:]])


def literal_kind(node):
    """A coarse TL type for an argument we can be sure about, else None."""
    if isinstance(node, ast.Constant):
        if isinstance(node.value, bool):
            return "Bool"
        if isinstance(node.value, bytes):
            return "bytes"
        if isinstance(node.value, int):
            return "int"
        if isinstance(node.value, str):
            return "string"

        return None

    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
        if node.func.id in ("bytes", "bytearray"):
            return "bytes"
        if node.func.id == "int":
            return "int"
        if node.func.id == "str":
            return "string"

        return None

    if isinstance(node, (ast.List, ast.Tuple)):
        kinds = {literal_kind(element) for element in node.elts}

        if len(kinds) == 1 and None not in kinds:
            return f"Vector<{kinds.pop()}>"

        return None

    if isinstance(node, ast.ListComp):
        kind = literal_kind(node.elt)

        return f"Vector<{kind}>" if kind else None

    return None


def dotted(node):
    parts = []

    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value

    if not isinstance(node, ast.Name):
        return None

    parts.append(node.id)

    return list(reversed(parts))


def local_kinds(scope):
    """Locals assigned exactly one recognisable literal, within one function.

    The argument is rarely a literal at the call site: send_poll built its
    correct_answers into a variable first, and passing the name is what hid the
    type error from a purely literal check.
    """
    assigned = {}

    for node in ast.walk(scope):
        if isinstance(node, ast.Assign):
            targets = [t for t in node.targets if isinstance(t, ast.Name)]
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            targets = [node.target]
        else:
            continue

        kind = literal_kind(node.value) if node.value is not None else None

        if kind is None:
            # an unrecognisable value, or a bare None for an optional field,
            # tells us nothing; it must not cancel a branch we could read
            continue

        for target in targets:
            assigned.setdefault(target.id, set()).add(kind)

    return {
        name: next(iter(kinds)) for name, kinds in assigned.items() if len(kinds) == 1
    }


def scopes(tree):
    """Each function body, plus the module for anything outside one."""
    functions = [
        node for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]

    return [*functions, tree]


def raw_arguments():
    """Every hand-written raw constructor argument we can type with confidence."""
    for path in sorted(PACKAGE.rglob("*.py")):
        if GENERATED in path.parents:
            continue

        tree = ast.parse(path.read_text(encoding="utf-8"))

        for scope in scopes(tree):
            known = local_kinds(scope)

            for node in ast.walk(scope):
                if not isinstance(node, ast.Call):
                    continue

                parts = dotted(node.func)

                if not parts or parts[0] != "raw" or len(parts) < 3:
                    continue

                if parts[1] not in ("types", "functions"):
                    continue

                info = TL.get(tl_name(parts[2:]))

                if info is None:
                    continue

                declared = {param["name"]: param["type"] for param in info["params"]}

                for keyword in node.keywords:
                    if keyword.arg is None:
                        continue

                    expected = declared.get(keyword.arg)
                    actual = literal_kind(keyword.value)

                    if actual is None and isinstance(keyword.value, ast.Name):
                        actual = known.get(keyword.value.id)

                    if expected is None or actual is None:
                        continue

                    yield (
                        str(path.relative_to(ROOT)),
                        keyword.value.lineno,
                        ".".join(parts[1:]),
                        keyword.arg,
                        expected,
                        actual,
                    )


def mismatched():
    for path, lineno, target, field, expected, actual in raw_arguments():
        expected_inner = re.fullmatch(r"Vector<(\w+)>", expected)
        actual_inner = re.fullmatch(r"Vector<(\w+)>", actual)

        if bool(expected_inner) != bool(actual_inner):
            continue

        if expected_inner:
            expected, actual = expected_inner.group(1), actual_inner.group(1)

        if expected not in SCALARS or actual not in SCALARS:
            continue

        if actual in COMPATIBLE.get(expected, {expected}):
            continue

        yield path, lineno, target, field, expected, actual


CASES = list(mismatched())


def test_the_schema_was_read():
    assert len(list(raw_arguments())) > 50, (
        "no raw constructor arguments were typed, so this check proves nothing; "
        "run `poe api` first"
    )


@pytest.mark.parametrize(
    "path,lineno,target,field,expected,actual",
    CASES,
    ids=[f"{t}.{f}" for _, _, t, f, _, _ in CASES]
)
def test_no_literal_contradicts_the_schema(path, lineno, target, field, expected, actual):
    """A literal of the wrong TL type only fails when the request is serialised.

    send_poll built its correct_answers as bytes long after layer 228 changed the
    field to Vector<int>, so every quiz poll died in Int.__new__ with 'bytes'
    object has no attribute 'to_bytes'.
    """
    pytest.fail(
        f"{path}:{lineno} passes {target}.{field} a {actual} "
        f"where the schema declares {expected}"
    )
