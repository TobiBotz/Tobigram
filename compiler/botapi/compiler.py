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
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from coverage import Coverage


def start():
    coverage = Coverage()
    findings = coverage.check()

    manifest = coverage.manifest
    supported = sum(
        len((manifest.get(k) or {}).get("supported") or []) for k in ("types", "methods")
    )
    pending = sum(
        len((manifest.get(k) or {}).get("pending") or {}) for k in ("types", "methods")
    )

    print(
        f"Bot API coverage: {coverage.spec['version']} | "
        f"{supported} supported, {pending} pending"
    )

    if not findings:
        print("  no drift")
        return

    for finding in findings:
        print(f"  {finding}")

    print(f"\n{len(findings)} coverage violation(s).")
    print("Add the parameter, record it in compiler/botapi/manifest.yaml, or")
    print("declare it unsupported in compiler/botapi/aliases.yaml.")

    raise SystemExit(1)


if "__main__" == __name__:
    start()
