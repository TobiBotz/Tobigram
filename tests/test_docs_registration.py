import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pyrogram

COMPILER = ROOT / "compiler" / "docs" / "compiler.py"

# Entries in the categories dicts sit at exactly twelve spaces
LISTED = set(re.findall(r"^\s{12}(\w+)$", COMPILER.read_text(encoding="utf-8"), re.M))

# Client attributes that are internal machinery rather than public API
INTERNAL_METHODS = {
    "authorize",
    "authorize_qr",
    "fetch_peers",
    "get_dc_option",
    "guess_extension",
    "guess_mime_type",
    "handle_download",
    "handle_updates",
    "load_plugins",
    "load_session",
    "media_pool_reaper",
    "get_file",
    "reap_media_sessions",
    "updates_watchdog",
}


def documented_alias_of(name):
    """Whether the attribute is another name for an already documented method.

    get_received_gifts is get_chat_gifts kept for compatibility; an alias needs
    no page of its own.
    """
    target = getattr(pyrogram.Client, name, None)

    return any(
        other != name
        and other in LISTED
        and getattr(pyrogram.Client, other, None) is target
        for other in dir(pyrogram.Client)
    )


def public_types():
    return sorted(
        name for name in dir(pyrogram.types)
        if isinstance(getattr(pyrogram.types, name), type)
        and issubclass(getattr(pyrogram.types, name), pyrogram.types.Object)
        and getattr(pyrogram.types, name) is not pyrogram.types.Object
    )


def public_enums():
    return sorted(pyrogram.enums.__all__)


@pytest.mark.parametrize("name", public_types())
def test_every_exported_type_is_documented(name):
    """A type exported but absent from the categories dict never renders.

    The docs compiler only emits what the dict names, so an exported class is
    silently missing from the site with nothing to notice it.
    """
    assert name in LISTED, (
        f"{name} is exported from pyrogram.types but has no entry in "
        f"compiler/docs/compiler.py, so it will not appear in the docs"
    )


@pytest.mark.parametrize("name", public_enums())
def test_every_exported_enum_is_documented(name):
    assert name in LISTED, (
        f"{name} is in pyrogram.enums.__all__ but has no entry in "
        f"compiler/docs/compiler.py"
    )


def test_every_public_client_method_is_documented():
    undocumented = sorted(
        name for name in dir(pyrogram.Client)
        if not name.startswith("_")
        and callable(getattr(pyrogram.Client, name, None))
        and name not in INTERNAL_METHODS
        and name not in LISTED
        and not documented_alias_of(name)
    )

    assert not undocumented, (
        "public Client methods with no entry in compiler/docs/compiler.py: "
        + ", ".join(undocumented)
    )


def test_the_categories_were_actually_read():
    assert len(LISTED) > 300, (
        "almost nothing was parsed out of the categories dicts, so these checks "
        "would pass whatever is missing"
    )
