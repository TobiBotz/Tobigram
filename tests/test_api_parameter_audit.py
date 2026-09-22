"""Automated audit test that dynamically discovers ALL methods and types from the project codebase

and verifies their parameters and fields against official Telegram API specifications without
any hardcoded lists.
"""

from __future__ import annotations

import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "compiler" / "botapi"))

from coverage import Coverage

COV = Coverage()


def get_all_project_methods():
    """Dynamically discover all Tobigram client methods mapped to official Bot API."""
    mapped = []
    spec_methods = COV.spec.get("methods", {})

    for tobi_name in sorted(COV.methods):
        for b_name in spec_methods:
            sym = COV.tobigram_method(b_name)
            if sym and sym.name == tobi_name:
                mapped.append((tobi_name, b_name))
                break

    return mapped


def get_all_project_types():
    """Dynamically discover all Tobigram types mapped to official Bot API."""
    mapped = []
    spec_types = COV.spec.get("types", {})

    for tobi_name in sorted(COV.types):
        for b_name in spec_types:
            sym = COV.tobigram_type(b_name)
            if sym and sym.name == tobi_name:
                mapped.append((tobi_name, b_name))
                break

    return mapped


ALL_METHODS = get_all_project_methods()
ALL_TYPES = get_all_project_types()


@pytest.mark.parametrize("tobi_name,botapi_name", ALL_METHODS, ids=[m[0] for m in ALL_METHODS])
def test_all_project_methods_parameters(tobi_name, botapi_name):
    """Automatically check that each project method has no unexpected missing parameters from official API."""
    manifest = COV.manifest.get("methods", {})
    supported_methods = set(manifest.get("supported", []))
    pending_methods = manifest.get("pending", {})

    botapi_gaps = set(COV.method_botapi_gaps(botapi_name) or [])

    if botapi_name in supported_methods:
        assert not botapi_gaps, (
            f"Method 'pyrogram.Client.{tobi_name}' (Official: {botapi_name}) is missing "
            f"parameters from official API: {sorted(botapi_gaps)}"
        )
    elif botapi_name in pending_methods:
        known_gaps = set((pending_methods[botapi_name] or {}).get("botapi", []))
        new_gaps = botapi_gaps - known_gaps
        assert not new_gaps, (
            f"Method 'pyrogram.Client.{tobi_name}' (Official: {botapi_name}) has NEW missing "
            f"parameters since manifest: {sorted(new_gaps)}"
        )


@pytest.mark.parametrize("tobi_name,botapi_name", ALL_TYPES, ids=[t[0] for t in ALL_TYPES])
def test_all_project_types_fields(tobi_name, botapi_name):
    """Automatically check that each project type has no unexpected missing fields from official API."""
    manifest = COV.manifest.get("types", {})
    supported_types = set(manifest.get("supported", []))
    pending_types = manifest.get("pending", {})

    gaps = set(COV.type_gaps(botapi_name) or [])

    if botapi_name in supported_types:
        assert not gaps, (
            f"Type 'pyrogram.types.{tobi_name}' (Official: {botapi_name}) is missing "
            f"fields from official API: {sorted(gaps)}"
        )
    elif botapi_name in pending_types:
        known_gaps = set((pending_types[botapi_name] or {}).get("botapi", []))
        new_gaps = gaps - known_gaps
        assert not new_gaps, (
            f"Type 'pyrogram.types.{tobi_name}' (Official: {botapi_name}) has NEW missing "
            f"fields since manifest: {sorted(new_gaps)}"
        )
