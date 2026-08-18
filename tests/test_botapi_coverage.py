import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "compiler" / "botapi"))

from coverage import (
    ENUM_REFERENCE_RE,
    Coverage,
    documented_params,
    enumerated_values,
)

COVERAGE = Coverage()
PACKAGE_SOURCES = [
    (path, path.read_text(encoding="utf-8"))
    for path in sorted((ROOT / "pyrogram").rglob("*.py"))
]

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


ALIAS_TARGETS = [
    (entity, spec_field, target)
    for entity, mapping in (
        ((COVERAGE.aliases.get("botapi") or {}).get("field_rename") or {}).items()
    )
    if entity != "*"
    for spec_field, target in mapping.items()
]


@pytest.mark.parametrize(
    "entity,spec_field,target",
    ALIAS_TARGETS,
    ids=[f"{e}.{f}" for e, f, _ in ALIAS_TARGETS]
)
def test_an_alias_target_is_populated_from_raw_data(entity, spec_field, target):
    """An alias claims wzgram already exposes the field under another name.

    Pointing at a parameter that nothing fills and nothing reads would satisfy
    the coverage check while the value is always None, which is worse than
    leaving the gap recorded.
    """
    symbol = COVERAGE.wzgram_type(entity)

    if symbol is None:
        pytest.skip(f"{entity} does not resolve")

    source = symbol.path.read_text(encoding="utf-8")
    name = re.escape(target)

    # filled from raw data by a _parse, or read back by a write()
    populated = re.search(rf"(?<!self\.)\b{name}\s*=\s*(?!{name}\b)", source)
    read_back = len(re.findall(rf"self\.{name}\b", source)) > 1

    # input types are filled by the caller and read by whoever sends them
    read_elsewhere = any(
        path != symbol.path and re.search(rf"(?<!self)\.{name}\b", text)
        for path, text in PACKAGE_SOURCES
    )

    assert populated or read_back or read_elsewhere, (
        f"{entity}.{spec_field} is aliased to {target}, but nothing fills "
        f"{target} from raw data and nothing ever reads it, so it is always None"
    )


def test_no_exclusion_masks_a_field_that_exists():
    """An exclusion must only ever cover a field wzgram genuinely lacks.

    Presence is checked before the unsupported table, so a field that is present
    counts as satisfied and stays checked. Letting the exclusion win first would
    mean removing Chat.type went unnoticed, since `type` is excluded globally for
    the union members that have no such field.
    """
    aliases = COVERAGE.aliases.get("botapi") or {}
    masked = []

    for table, resolve in (
        ("field_unsupported", COVERAGE.wzgram_type),
        ("method_field_unsupported", COVERAGE.wzgram_method),
    ):
        for entity, fields in (aliases.get(table) or {}).items():
            if entity == "*":
                continue

            symbol = resolve(entity)

            if symbol is None:
                continue

            for field in fields:
                gaps = (
                    COVERAGE.type_gaps(entity)
                    if resolve is COVERAGE.wzgram_type
                    else COVERAGE.method_botapi_gaps(entity)
                )

                if gaps is not None and field not in gaps and field in symbol.params:
                    masked.append(f"{entity}.{field}")

    assert not masked, (
        "these are excluded yet present, so the exclusion is doing the work "
        "instead of the field: " + ", ".join(sorted(masked))
    )


def test_every_exclusion_carries_a_reason():
    aliases = COVERAGE.aliases.get("botapi") or {}
    blank = []

    for table in ("type_unsupported", "method_unsupported"):
        blank += [
            f"{table}.{name}"
            for name, reason in (aliases.get(table) or {}).items()
            if not str(reason).strip()
        ]

    for table in ("field_unsupported", "method_field_unsupported"):
        for entity, fields in (aliases.get(table) or {}).items():
            blank += [
                f"{entity}.{field}"
                for field, reason in fields.items()
                if not str(reason).strip()
            ]

    assert not blank, "excluded without saying why: " + ", ".join(sorted(blank))


def test_no_rename_points_at_itself():
    tables = [
        (COVERAGE.aliases.get("botapi") or {}).get("field_rename") or {},
        (COVERAGE.aliases.get("botapi") or {}).get("method_field_rename") or {},
        (COVERAGE.aliases.get("mtproto") or {}).get("field_rename") or {},
    ]
    pointless = [
        f"{entity}.{source}"
        for table in tables
        for entity, mapping in table.items()
        for source, target in mapping.items()
        if source == target
    ]

    assert not pointless, "renamed to itself: " + ", ".join(sorted(pointless))


def test_the_enum_axis_actually_resolves_enums():
    """A broken reference pattern makes every enum field silently unresolvable.

    The axis then reports full coverage while checking nothing, which is how it
    first passed with a corrupted pattern.
    """
    assert ENUM_REFERENCE_RE.findall("'enums.MessageEntityType'") == ["MessageEntityType"]
    assert ENUM_REFERENCE_RE.findall("ButtonStyle") == ["ButtonStyle"]

    symbol = COVERAGE.wzgram_type("MessageEntity")

    assert symbol.annotations.get("type"), "annotations must be captured from the AST"
    assert "MessageEntityType" in COVERAGE.enums


def test_enumerated_values_are_read_from_the_description():
    field = next(
        f for f in COVERAGE.spec["types"]["MessageEntity"]["fields"]
        if f["name"] == "type"
    )

    assert len(enumerated_values(field)) > 15, (
        "Bot API only spells a field's accepted values in its description, so "
        "failing to read them leaves the enum axis with nothing to check"
    )


ENUM_CASES = [
    (kind, name)
    for kind in ("types", "methods")
    for name in COVERAGE.implemented(kind)
]


@pytest.mark.parametrize(
    "kind,name", ENUM_CASES, ids=[f"{k[:-1]}.{n}" for k, n in ENUM_CASES]
)
def test_enum_members_cover_the_documented_values(kind, name):
    recorded = set(
        ((COVERAGE.manifest[kind].get("pending") or {}).get(name) or {}).get("enums") or []
    )
    gaps = set(COVERAGE.enum_gaps(kind, name) or [])

    assert gaps <= recorded, (
        f"{name} accepts documented values with no enum member: "
        + ", ".join(sorted(gaps - recorded))
    )
