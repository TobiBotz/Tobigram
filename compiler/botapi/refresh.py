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

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from coverage import MANIFEST_PATH, SPEC_PATH, Coverage, load_spec

API_URL = "https://core.telegram.org/bots/api"

VERSION_RE = re.compile(r"^Bot API \d+\.\d+$")

MIN_METHODS = 100
MIN_TYPES = 100

HEADER = """\
# Bot API coverage manifest.
#
# supported: every Bot API and MTProto parameter must be present. The build
#            fails otherwise.
# pending:   the gaps recorded when the entry was last surveyed. The build fails
#            if the list grows, if a recorded gap is no longer missing, or if it
#            empties without being promoted to supported.
#
# Absent Bot API types and methods are deliberate and are not listed here.
# Regenerate the pending section with: uv run poe botapi-refresh
"""


def scrape() -> dict:
    try:
        import scrape as scraper
    except ImportError as e:
        raise SystemExit(
            f"the scraper needs {e.name}: uv sync --extra botapi, or pass --offline "
            f"to re-survey the vendored copy of the spec"
        ) from None

    print(f"Scraping {API_URL}")
    spec = scraper.retrieve_info(API_URL)

    if scraper.verify_type_parameters(spec) or scraper.verify_method_parameters(spec):
        raise SystemExit("the scraped schema does not validate; see the log above")

    return spec


def sanity_check(spec: dict):
    """Refuse a scrape that would replace the vendored spec with something worse.

    The spec is vendored so that a Bot API release cannot spontaneously turn the
    build red. Overwriting it with a redirect, an error page or a spec whose
    shape has changed under the scraper gives up exactly that, and the damage is
    only visible a compiler run later.
    """

    version = spec.get("version") or ""

    if not VERSION_RE.match(version):
        raise SystemExit(f"scraped version {version!r} is not a Bot API version")

    methods, types = len(spec.get("methods") or {}), len(spec.get("types") or {})

    if methods < MIN_METHODS or types < MIN_TYPES:
        raise SystemExit(
            f"scraped {methods} methods and {types} types, which is too few to be "
            f"the whole page"
        )

    if not SPEC_PATH.exists():
        return

    current = load_spec()
    vendored = len(current.get("methods") or {}), len(current.get("types") or {})

    if methods < vendored[0] or types < vendored[1]:
        raise SystemExit(
            f"scraped {methods} methods and {types} types against the vendored "
            f"{vendored[0]} and {vendored[1]}; Bot API does not remove them, so the page "
            f"or the scraper has changed shape"
        )


def write(spec: dict):
    sanity_check(spec)

    current = load_spec()["version"] if SPEC_PATH.exists() else None
    SPEC_PATH.write_text(json.dumps(spec), encoding="utf-8")

    print(f"  {spec['version']} ({spec['release_date']})"
          f"{'' if current is None else f', was {current}'}")
    print(f"  wrote {SPEC_PATH.relative_to(SPEC_PATH.parents[3])} "
          f"({SPEC_PATH.stat().st_size} bytes)")


def survey(coverage: Coverage) -> dict:
    manifest = {"version": coverage.spec["version"], "release_date": coverage.spec["release_date"]}

    for kind, names in (
        ("types", coverage.spec["types"]),
        ("methods", coverage.spec["methods"]),
    ):
        supported, pending = [], {}

        for name in sorted(names):
            if kind == "types":
                botapi, mtproto = coverage.type_gaps(name), None
            else:
                botapi = coverage.method_botapi_gaps(name)
                mtproto = coverage.method_mtproto_gaps(name)

            enums_ = coverage.enum_gaps(kind, name)

            if botapi is None and mtproto is None and enums_ is None:
                continue

            gaps = {}

            if botapi:
                gaps["botapi"] = sorted(botapi)

            if mtproto:
                gaps["mtproto"] = sorted(mtproto)

            if enums_:
                gaps["enums"] = sorted(enums_)

            if gaps:
                pending[name] = gaps
            else:
                supported.append(name)

        manifest[kind] = {"supported": supported, "pending": pending}
        print(f"  {kind}: {len(supported)} supported, {len(pending)} pending")

    return manifest


def dump(manifest: dict) -> str:
    lines = [HEADER, f"version: {manifest['version']!r}", f"release_date: {manifest['release_date']!r}"]

    for kind in ("types", "methods"):
        entry = manifest[kind]
        lines.append(f"\n{kind}:")
        lines.append("  supported:")

        for name in entry["supported"]:
            lines.append(f"    - {name}")

        if not entry["supported"]:
            lines.append("    []")

        lines.append("  pending:")

        for name, gaps in entry["pending"].items():
            lines.append(f"    {name}:")

            for axis in ("botapi", "mtproto", "enums"):
                if gaps.get(axis):
                    lines.append(f"      {axis}: [{', '.join(gaps[axis])}]")

        if not entry["pending"]:
            lines.append("    {}")

    return "\n".join(lines) + "\n"


def start(fetch: bool = True):
    if fetch:
        write(scrape())

    coverage = Coverage()
    print(f"Surveying against {coverage.spec['version']}")
    manifest = survey(coverage)
    MANIFEST_PATH.write_text(dump(manifest), encoding="utf-8")
    print(f"  wrote {MANIFEST_PATH.name}")


if "__main__" == __name__:
    start(fetch="--offline" not in sys.argv)
