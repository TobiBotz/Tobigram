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


def pct(part, whole):
    return f"{100.0 * part / whole:5.1f}%" if whole else "    - "


def start():
    coverage = Coverage()
    report = coverage.report()
    methods, types = report["methods"], report["types"]

    print(f"Bot API coverage - {coverage.spec['version']} ({coverage.spec['release_date']})")
    print()
    print("Methods")
    print(f"  implemented       {methods['implemented']:5} / {methods['total']:<5} "
          f"{pct(methods['implemented'], methods['total'])}")

    have, total = methods["params"]
    print(f"  Bot API params    {have:5} / {total:<5} {pct(have, total)}"
          f"   {total - have} missing across {methods['incomplete']} methods")

    have, total = methods["tl_params"]
    print(f"  MTProto params    {have:5} / {total:<5} {pct(have, total)}"
          f"   {total - have} missing")

    have, total = report["enums"]["values"]
    print(f"  enum values       {have:5} / {total:<5} {pct(have, total)}"
          f"   {total - have} missing")

    print()
    print("Types reachable from those methods")
    print(f"  required          {types['required']:5}")
    print(f"  implemented       {types['implemented']:5} / {types['required']:<5} "
          f"{pct(types['implemented'], types['required'])}"
          f"   {len(types['absent'])} absent")

    have, total = types["params"]
    print(f"  Bot API params    {have:5} / {total:<5} {pct(have, total)}"
          f"   {total - have} missing")

    if types["absent"]:
        print()
        print(f"  Required but not implemented ({len(types['absent'])}):")

        for name in types["absent"]:
            print(f"    {name}")

    print()
    print(f"  {types['unreachable']} further spec types are unreachable from the "
          f"implemented methods and are not tracked.")

    print()
    print("Largest gaps (Bot API parameters missing | TL fields not exposed)")

    pending = []

    for kind in ("methods", "types"):
        for name, gaps in ((coverage.manifest.get(kind) or {}).get("pending") or {}).items():
            botapi = gaps.get("botapi") or []
            mtproto = gaps.get("mtproto") or []
            pending.append((len(botapi) + len(mtproto), kind, name, botapi, mtproto))

    for _, kind, name, botapi, mtproto in sorted(pending, reverse=True)[:12]:
        print(f"  {kind[:-1]:6} {name}")

        if botapi:
            print(f"           bot api  {', '.join(botapi)}")

        if mtproto:
            print(f"           mtproto  {', '.join(mtproto)}")

    manifest = coverage.manifest
    supported = sum(
        len((manifest.get(k) or {}).get("supported") or []) for k in ("types", "methods")
    )
    pending = sum(
        len((manifest.get(k) or {}).get("pending") or {}) for k in ("types", "methods")
    )

    print()
    print(f"Manifest            {supported} supported, {pending} pending")
    print()

    findings = coverage.check()

    if not findings:
        print("No drift.")
        return

    for finding in findings:
        print(f"  {finding}")

    print()
    print(f"{len(findings)} coverage violation(s).")
    print("Add the parameter, record it in compiler/botapi/manifest.yaml, or")
    print("declare it unsupported in compiler/botapi/aliases.yaml.")

    raise SystemExit(1)


if "__main__" == __name__:
    start()
