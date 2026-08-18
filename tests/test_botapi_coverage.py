import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "compiler" / "botapi"))

from coverage import Coverage, documented_params

COVERAGE = Coverage()

MANIFEST_FINDINGS = COVERAGE.check_manifest()
DOCSTRING_FINDINGS = COVERAGE.check_docstrings()


def entities(kind):
    entry = COVERAGE.manifest.get(kind) or {}

    return sorted(
        set(entry.get("supported") or []) | set(entry.get("pending") or {})
    )


def findings_for(entity):
    return [f for f in MANIFEST_FINDINGS if f.entity.endswith(f"/{entity}")]


def test_the_manifest_records_a_spec_version():
    assert COVERAGE.manifest.get("version") == COVERAGE.spec["version"], (
        "manifest.yaml was surveyed against a different Bot API release than "
        "compiler/botapi/source/botapi.json ships; run `poe botapi-refresh`"
    )


@pytest.mark.parametrize("name", entities("types"))
def test_type_matches_the_manifest(name):
    problems = findings_for(name)

    assert not problems, "\n".join(str(p) for p in problems)


@pytest.mark.parametrize("name", entities("methods"))
def test_method_matches_the_manifest(name):
    problems = findings_for(name)

    assert not problems, "\n".join(str(p) for p in problems)


def test_no_manifest_finding_is_unattributed():
    attributed = {f.entity.split("/", 1)[1] for f in MANIFEST_FINDINGS if "/" in f.entity}
    known = set(entities("types")) | set(entities("methods"))
    orphans = [f for f in MANIFEST_FINDINGS if "/" not in f.entity]

    assert not orphans, "\n".join(str(f) for f in orphans)
    assert attributed <= known, (
        "a finding names an entity absent from the manifest, so no "
        "parametrized case would report it: " + ", ".join(sorted(attributed - known))
    )


@pytest.mark.parametrize(
    "name,detail",
    [(f.entity, f.detail) for f in DOCSTRING_FINDINGS],
    ids=[f.entity for f in DOCSTRING_FINDINGS]
)
def test_docstring_matches_the_signature(name, detail):
    pytest.fail(f"{name}: {detail}")


def test_comma_grouped_parameters_are_understood():
    doc = """
    Parameters:
        old_title, new_title (``str``, *optional*):
            Title before and after.

        solo (``int``):
            One.
    """

    assert documented_params(doc) == {"old_title", "new_title", "solo"}, (
        "several types document a before/after pair on one line; reading only "
        "the first name reports every parameter in the block as undocumented"
    )


def test_the_docstring_axis_actually_reads_docstrings():
    symbol = COVERAGE.types["KeyboardButton"]

    assert documented_params(symbol.doc), (
        "ast.get_docstring dedents by default, which silently stops the "
        "Parameters: block from matching and makes the whole docstring axis "
        "pass without checking anything"
    )
    assert "text" in documented_params(symbol.doc)


def test_unsupported_entries_are_kept_out_of_the_manifest():
    aliases = COVERAGE.aliases.get("botapi") or {}
    declared = set(aliases.get("type_unsupported") or {}) | set(
        aliases.get("method_unsupported") or {}
    )
    tracked = set(entities("types")) | set(entities("methods"))

    assert declared, "aliases.yaml should declare the Bot API surface MTProto lacks"
    assert not declared & tracked, (
        "these are declared unsupported but still surveyed, so the reason "
        "recorded against them does nothing: "
        + ", ".join(sorted(declared & tracked))
    )
