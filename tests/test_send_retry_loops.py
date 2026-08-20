import ast
from pathlib import Path

import pytest

METHODS = Path(__file__).resolve().parents[1] / "pyrogram" / "methods"


def _handler_names(handler):
    node = handler.type

    if node is None:
        return []

    parts = node.elts if isinstance(node, ast.Tuple) else [node]

    return [p.id if isinstance(p, ast.Name) else getattr(p, "attr", "") for p in parts]


def _retry_loops():
    for path in sorted(METHODS.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))

        for node in ast.walk(tree):
            if not isinstance(node, ast.While):
                continue

            if not (isinstance(node.test, ast.Constant) and node.test.value is True):
                continue

            for child in ast.walk(node):
                if not isinstance(child, ast.Try) or not child.orelse:
                    continue

                if any("FilePartMissing" in _handler_names(h) for h in child.handlers):
                    yield path, child


def _cases():
    return [pytest.param(p, t, id=f"{p.parent.name}/{p.stem}:{t.lineno}") for p, t in _retry_loops()]


def test_the_retry_loops_are_still_there():
    assert len(_cases()) >= 10, (
        "this file guards the upload-retry loops; if they are gone the guard is "
        "checking nothing"
    )


@pytest.mark.parametrize("path,try_node", [(p.values[0], p.values[1]) for p in _cases()],
                         ids=[p.id for p in _cases()])
def test_a_successful_send_is_never_retried(path, try_node):
    # `while True` is there to re-send after FilePartMissing and nothing else. If
    # the success branch can fall off the end - the server answered with an
    # Updates carrying none of the update types the method looks for, which is
    # what a business connection or a suggested post does - the loop sends the
    # very same media again, and again, for as long as that keeps happening.
    last = try_node.orelse[-1]

    assert isinstance(last, (ast.Return, ast.Raise, ast.Break)), (
        f"{path.name}: the success branch of the retry loop ends in "
        f"{type(last).__name__}, so an answer it does not recognise re-sends the "
        "message forever"
    )
