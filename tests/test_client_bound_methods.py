import ast
import pathlib

import pytest

import pyrogram

PACKAGE = pathlib.Path(pyrogram.__file__).parent


def bound_calls():
    for path in sorted((PACKAGE / "types").rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
                continue
            owner = node.func.value
            if (isinstance(owner, ast.Attribute)
                    and owner.attr in ("_client", "client")
                    and isinstance(owner.value, ast.Name)
                    and owner.value.id == "self"):
                yield path.relative_to(PACKAGE.parent), node.lineno, node.func.attr


@pytest.mark.parametrize(
    "path,lineno,name",
    list(bound_calls()),
    ids=lambda v: str(v)
)
def test_bound_method_target_exists(path, lineno, name):
    assert hasattr(pyrogram.Client, name), (
        f"{path}:{lineno} calls self._client.{name}(), which Client does not define"
    )
