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

import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from coverage import MANIFEST_PATH, SPEC_PATH, Coverage

SPEC_URL = (
    "https://raw.githubusercontent.com/PaulSonOfLars/"
    "telegram-bot-api-spec/main/api.min.json"
)

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


def download():
    print(f"Fetching {SPEC_URL}")
    payload = urllib.request.urlopen(SPEC_URL).read()
    SPEC_PATH.write_bytes(payload)
    print(f"  wrote {SPEC_PATH.relative_to(SPEC_PATH.parents[3])} ({len(payload)} bytes)")


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

            if botapi is None and mtproto is None:
                continue

            gaps = {}

            if botapi:
                gaps["botapi"] = sorted(botapi)

            if mtproto:
                gaps["mtproto"] = sorted(mtproto)

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

            for axis in ("botapi", "mtproto"):
                if gaps.get(axis):
                    lines.append(f"      {axis}: [{', '.join(gaps[axis])}]")

        if not entry["pending"]:
            lines.append("    {}")

    return "\n".join(lines) + "\n"


def start(fetch: bool = True):
    if fetch:
        download()

    coverage = Coverage()
    print(f"Surveying against {coverage.spec['version']}")
    manifest = survey(coverage)
    MANIFEST_PATH.write_text(dump(manifest), encoding="utf-8")
    print(f"  wrote {MANIFEST_PATH.name}")


if "__main__" == __name__:
    start(fetch="--offline" not in sys.argv)
